from elasticsearch import AsyncElasticsearch, helpers

from .api.v1.schemas import (
    BulkInsertSchema,
    ErrorDetailSchema,
    InsertSummarySchema,
    SingleInsertSchema,
)


class IngestorElkQry:
    def __init__(self, db: AsyncElasticsearch):
        self.db = db

    async def insert_doc(self, log_data: dict, index_name: str) -> SingleInsertSchema:

        index_params = {
            "index": index_name,
            "document": log_data,
            "id": log_data.pop("_id", None)
        }

        response = await self.db.index(**index_params)
        return SingleInsertSchema(success=True, **response.body)

    async def bulk_insert_docs(
        self, logs_data: list[dict], index_name: str, batch_size: int = 1000
    ) -> BulkInsertSchema:
        actions = (
            {
                "_op_type": "index",
                "_index": index_name,
                "_source": doc,
                "_id": doc.pop("_id", None),
            }
            for doc in logs_data
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
                errors.append(self._extract_error_info(info))

        return BulkInsertSchema(
            success=summary["failed"] == 0,
            summary=InsertSummarySchema(**summary),
            errors=[ErrorDetailSchema(**err) for err in errors]
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
