from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from apps.analytic.query import AnalyticElkQry
from apps.analytic.repository import AnalyticRepo
from config.settings.services.elk import get_read_es_client


async def get_analytic_log_elk_query(db: AsyncElasticsearch = Depends(get_read_es_client)):
    """
    Database coupling is isolated to the query layer.
    """
    return AnalyticElkQry(db)


async def get_analytic_log_repo(
    elk_qry: AnalyticElkQry = Depends(get_analytic_log_elk_query),
) -> AnalyticRepo:
    """
    Dependency function to get the repository with query layer injection.
    """
    return AnalyticRepo(elk_qry)
