from fastapi import Depends, APIRouter, HTTPException, status, Response

from apps.ingestor.repository import IngestorRepo
from config.settings.services.log import setup_logging
from .dependencies import get_ingestor_repo
from .schemas import BulkInsertSchema, SingleInsertSchema

logger = setup_logging()


v1_router = APIRouter(
    prefix="/ingestor/api/v1/index",
    tags=["v1_ingestor"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation Error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)

__all__ = ["v1_router"]


@v1_router.post(
    path="/{index_name}/store-doc",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleInsertSchema,
    summary="Create a single doc in index you want",
    description="Insert a single document into Elasticsearch",
)
async def store_doc(
    index_name: str,
    log_data: dict,
    repo: IngestorRepo = Depends(get_ingestor_repo),
) -> SingleInsertSchema:
    try:
        response = await repo.insert_doc(log_data, index_name)
        logger.info("doc inserted successfully", extra={"data": response.model_dump()})
        return response
    except Exception as e:
        logger.exception("error inserting doc", extra={"data": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating the log entry",
        )



@v1_router.post(
    "/{index_name}/store-docs",
    response_model=BulkInsertSchema,
    summary="Bulk create doc entries",
    description="Insert multiple log documents into Elasticsearch in bulk",
    responses={
        status.HTTP_201_CREATED: {
            "description": "All documents inserted successfully",
            "model": BulkInsertSchema,
        },
        status.HTTP_207_MULTI_STATUS: {
            "description": "Partial success - some documents inserted, some failed",
            "model": BulkInsertSchema,
        },
        status.HTTP_417_EXPECTATION_FAILED: {
            "description": "All documents failed to insert",
            "model": BulkInsertSchema,
        },
    },
)
async def bulk_store_docs(
    response: Response,
    log_data: list[dict],
    index_name: str,
    repo: IngestorRepo = Depends(get_ingestor_repo),
) -> BulkInsertSchema:
    try:
        result = await repo.bulk_insert_docs(log_data, index_name)

        if result.summary.failed == 0:
            response.status_code = status.HTTP_201_CREATED
        elif result.summary.inserted > 0:
            response.status_code = status.HTTP_207_MULTI_STATUS
        else:
            response.status_code = status.HTTP_417_EXPECTATION_FAILED

        logger.info("bulk docs processed", extra={"data": result.model_dump()})

        return result

    except Exception as e:
        logger.exception("error bulk inserting docs", extra={"data": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while bulk creating log entries",
        )
