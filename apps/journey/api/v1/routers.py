from typing import Annotated, Any, Dict
from elasticsearch import AsyncElasticsearch, BadRequestError
from fastapi import Body, Depends, APIRouter, HTTPException, Query, status

from apps.journey.query import ElasticSearchQry
from apps.journey.repository import JourneyRepo
from config.settings.services.elk import get_read_es_client, get_write_es_client
from config.settings.services.log import setup_logging
from .schemas import DynamicDoc, ESResponse, InsertResultSchema, JourneyQuerySchema, PaginatedResponse, UpdateInputSchema, UpdateResultSchema

logger = setup_logging()


v1_router = APIRouter(
    prefix="/journey/api/v1",
    tags=["v1_journey"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation Error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)

__all__ = ["v1_router"]

index_name = "journey_v3"
historical_index_name = "historical_journey_v1"


@v1_router.get(
    "/get_by_id",
    response_model=DynamicDoc | None,
    summary="Bulk create doc entries",
    description="Insert multiple log documents into Elasticsearch in bulk",
)
async def get_by_id(
    id: Annotated[str, Query(title="Query string", description="Query string for the items to search in the database that have a good match")],
    db: AsyncElasticsearch = Depends(get_read_es_client)
) -> DynamicDoc | None:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.get_journey_by_id(id)
        if result:
            return DynamicDoc(id=result["_id"], source=result["_source"])
        return None

    except Exception as e:
        logger.exception("error get doc", extra={"data": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating entries",
        )


@v1_router.post(
    "/save",
    response_model=InsertResultSchema,
    summary="single create doc entries",
    description="Insert single documents into Elasticsearch ",
)
async def save(
    input: Annotated[Dict[str, Any], Body(title="body string", description="body json for the items to save in the database")],
    db: AsyncElasticsearch = Depends(get_write_es_client)
) -> InsertResultSchema:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.save_journey(input)
        return result

    except BadRequestError as e:
        logger.warning("Bad request while inserting doc",
                       extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format or field type: {e.error}"
        )
    except Exception as e:
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected internal server error"
        )


@v1_router.patch(
    "/update/{id}",
    response_model=UpdateResultSchema,
    summary="single update doc entries",
    description="update single documents",
)
async def update(
    input: Annotated[UpdateInputSchema, Body(title="body string", description="body json for the items to save in the database")],
    id: str,
    db: AsyncElasticsearch = Depends(get_write_es_client)
) -> UpdateResultSchema:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.update_journey(id, input)
        return result

    except BadRequestError as e:
        logger.warning("Bad request while inserting doc",
                       extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format or field type: {e.error}"
        )
    except Exception as e:
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected internal server error"
        )


@v1_router.post(
    "/bulk-save",
    response_model=InsertResultSchema,
    summary="Bulk create doc entries",
    description="Insert multiple log documents into Elasticsearch in bulk",
)
async def bulk_save(
    inputs: Annotated[list[Dict[str, Any]], Body(title="body string", description="body json for the items to save in the database")],
    db: AsyncElasticsearch = Depends(get_write_es_client)
) -> InsertResultSchema:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.save_journeys(inputs)
        return result

    except BadRequestError as e:
        logger.warning("Bad request while inserting doc",
                       extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format or field type: {e.error}"
        )
    except Exception as e:
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected internal server error"
        )


@v1_router.get(
    "/all",
    response_model=ESResponse,
    summary="Bulk create doc entries",
    description="Insert multiple log documents into Elasticsearch in bulk",
)
async def all(
    db: AsyncElasticsearch = Depends(get_read_es_client)
) -> ESResponse:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.all_journeys()
        return result

    except BadRequestError as e:
        logger.warning("Bad request while inserting doc",
                       extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format or field type: {e.error}"
        )
    except Exception as e:
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected internal server error"
        )


@v1_router.post(
    "/search",
    response_model=ESResponse | None,
    summary="search doc entries",
    description="search multiple  documents from Elasticsearch",
)
async def search(
    query_data: JourneyQuerySchema = Body(...),
    db: AsyncElasticsearch = Depends(get_read_es_client)
) -> ESResponse | None:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.search_journey(query_data=query_data)
        return result

    except BadRequestError as e:
        logger.warning("Bad request while inserting doc",
                       extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format or field type: {e.error}"
        )
    except Exception as e:
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected internal server error"
        )


@v1_router.get(
    "/all-paginated",
    response_model=PaginatedResponse,
    summary="Bulk create doc entries",
    description="Insert multiple log documents into Elasticsearch in bulk",
)
async def all_paginated(
    size: Annotated[int | None, Query(
        title="query size", description="body json for the items to save in the database")] = 10,
    page: Annotated[int | None, Query(
        title="query page", description="body json for the items to save in the database")] = 1,
    db: AsyncElasticsearch = Depends(get_read_es_client)
) -> PaginatedResponse:
    try:
        repo = JourneyRepo(ElasticSearchQry(db=db, index_name=index_name))
        result = await repo.all_journeys_with_pagination(page=page, size=size)
        return result

    except BadRequestError as e:
        logger.warning("Bad request while inserting doc",
                       extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format or field type: {e.error}"
        )
    except Exception as e:
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected internal server error"
        )
