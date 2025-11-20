from abc import ABC, abstractmethod
from datetime import datetime
from elasticsearch import AsyncElasticsearch, NotFoundError, helpers
from typing import List, Optional, TypeVar
from config.settings.services.log import setup_logging

from pydantic import BaseModel

from .api.v1.schemas import (
    ESResponse,
    ErrorDetailSchema,
    InsertResultSchema,
    InsertSummarySchema,
    PaginatedResponse,
    PaginationMeta,
    UpdateResultSchema,
    UpdateSummarySchema,
)
logger = setup_logging()

T = TypeVar("T", bound=BaseModel)


class BaseQuery(ABC):
    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Optional[T]:
        """Get a single record/document by its ID."""
        pass

    @abstractmethod
    async def search(self, query: dict) -> ESResponse:
        """Perform a search or query operation."""
        pass

    @abstractmethod
    async def all_paginated(self, page: int = 1, size: int = 10) -> PaginatedResponse:
        """Perform a search or query operation."""
        pass

    @abstractmethod
    async def all(self) -> ESResponse:
        """Perform a search or query operation."""
        pass

    @abstractmethod
    async def count(self, query: Optional[dict] = None) -> int:
        """Return count of matching records/documents."""
        pass

    @abstractmethod
    async def create_collection(self, collection_name: str) -> bool:
        """Return count of matching records/documents."""
        pass

    @abstractmethod
    async def update(self, id: str, input: T) -> UpdateResultSchema:
        """Save a single domain object and return its ID."""
        pass

    @abstractmethod
    async def save(self, data: T) -> InsertResultSchema:
        """Save a single domain object and return its ID."""
        pass

    @abstractmethod
    async def bulk_save(self, data_list: List[T]) -> InsertResultSchema:
        """Save multiple objects, returning successes and failures."""
        pass


class ElasticSearchQry(BaseQuery):
    def __init__(self, db: AsyncElasticsearch, index_name: str):
        self.db = db
        self.index_name = index_name

    async def get_by_id(self, doc_id: str) -> Optional[T]:
        try:
            res = await self.db.get(index=self.index_name, id=doc_id)
            return res
        except NotFoundError:
            return None
        except Exception as e:
            print(str(e))

    async def search(self, query: dict) -> list[T]:
        try:
            res = await self.db.search(index=self.index_name, body=query)
            hits = res["hits"]["hits"]
            docs = [hit for hit in hits]
            total = res["hits"]["total"]["value"]
            return ESResponse(
                total=total,
                hits=docs
            )
        except Exception as e:
            print(f"Error searching documents: {e}")
            return ESResponse(
                total=0,
                hits=[]
            )
        
    async def count(self, query: Optional[dict] = None) -> int:
        """Return count of matching records/documents."""
        pass

    async def create_collection(self, collection_name: str) -> bool:
        """Return count of matching records/documents."""
        pass

    async def _log(self, id, meta):
        historical_index = f'historical_{self.index_name}'
        try:
            current_doc = await self.db.get(index=self.index_name, id=id)
        except Exception as e:
            logger.warning("document has not been found",
                           extra={"error": str(e)})
            current_doc = None

        if current_doc and current_doc.get("_source"):
            hist_doc = current_doc["_source"].copy()
            hist_doc["_original_id"] = id
            hist_doc.update(meta)
            
            try:
                await self.db.index(index=historical_index, document=hist_doc)
                return True
            except Exception as e:
                return False
        return False

    async def update(self, id: str, input: T) -> UpdateResultSchema:
        index_params = {
            "index": self.index_name,
            "id": id,
            "doc": input.data,
        }
        summary_success = {"updated": 1, "failed": 0}
        summary_error = {"updated": 0, "failed": 1}
        result = await self._log(id, input.meta)
        if result:
            response = await self.db.update(**index_params)
            return UpdateResultSchema(success=True, summary=UpdateSummarySchema(**summary_success), errors=None)
        return UpdateResultSchema(success=False, summary=UpdateSummarySchema(**summary_error), errors=None)

    async def save(self, data: T) -> InsertResultSchema:
        index_params = {
            "index": self.index_name,
            "document": data,
            "id": data.get("id", None)
        }
        summary = {"inserted": 1, "failed": 0}
        response = await self.db.index(**index_params)

        return InsertResultSchema(success=True, summary=InsertSummarySchema(**summary), errors=None)

    async def bulk_save(self, data_list: List[T], batch_size: int = 1000) -> InsertResultSchema:
        actions = (
            {
                "_op_type": "index",
                "_index": self.index_name,
                "_source": doc,
                "_id": doc.get("_id", None),
            }
            for doc in data_list
        )

        summary = {"inserted": 0, "failed": 0}
        errors = []

        async for ok, info in helpers.async_streaming_bulk(
            client=self.db,
            actions=actions,
            chunk_size=batch_size,
            raise_on_error=False,
        ):
            if ok:
                summary["inserted"] += 1
            else:
                summary["failed"] += 1
                errors.append(info)

        return InsertResultSchema(
            success=summary["failed"] == 0,
            summary=InsertSummarySchema(**summary),
            errors=[ErrorDetailSchema(
                **self._extract_error_info(err)) for err in errors]
        )

    async def all_paginated(self, page: int = 1, size: int = 10) -> PaginatedResponse:
        from_ = (page - 1) * size
        response = await self.db.search(
            index=self.index_name,
            body={"query": {"match_all": {}}},
            from_=from_,
            size=size,
        )
        docs = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]
        return PaginatedResponse(
            meta=PaginationMeta(page=page, size=size, total=total),
            results=docs
        )

    async def all(self) -> ESResponse:
        response = await self.db.search(
            index=self.index_name,
            body={"query": {"match_all": {}}})
        docs = [hit for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]
        return ESResponse(
            total=total,
            hits=docs
        )

    @staticmethod
    def _extract_error_info(info: dict) -> dict:
        failed_doc = info.get("index", {})
        error_info = failed_doc.get("error", {})

        reason = (
            error_info.get("reason")
            or error_info.get("caused_by", {}).get("reason")
            or str(error_info)
        )

        return {
            "id": failed_doc.get("_id"),
            "reason": reason,
        }