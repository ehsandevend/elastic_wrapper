from fastapi import Depends, APIRouter, HTTPException, status, Query
from starlette.responses import JSONResponse

from config.settings.services.log import setup_logging
from .dependencies import get_analytic_log_repo
from ...repository import AnalyticRepo

logger = setup_logging()


# Export this for auto-discovery
v1_router = APIRouter(
    prefix="/analytic/api/v1",
    tags=["v1_analytic"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation Error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)

__all__ = ["v1_router"]


@v1_router.get("/claims/flow")
async def get_claim_flow(
    eclaim_id: int | None = Query(None, description="Electronic claim ID"),
    document_id: int | None = Query(None, description="Document ID"),
    claim_id: int | None = Query(None, description="Calim ID"),
    repo: AnalyticRepo = Depends(get_analytic_log_repo),
):
    """
    Retrieve analytic claim flow by either eclaim_id or document_id.
    One of the two parameters must be provided.
    """
    if not eclaim_id and not document_id and not claim_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either eclaim_id or document_id or claim_id in query params",
        )

    try:
        if eclaim_id:
            result = await repo.get_claim_flow_by_eclaim_id(eclaim_id)
        elif document_id:
            result = await repo.get_claim_flow_by_document_id(document_id)
        else:
            result = await repo.get_claim_flow_by_claim_id(claim_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        logger.exception("Error retrieving claim flow", extra={"data": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
