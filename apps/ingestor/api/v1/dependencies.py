from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from apps.ingestor.query import IngestorElkQry
from apps.ingestor.repository import IngestorRepo
from config.settings.services.elk import get_write_es_client


async def get_ingestor_elk_query(db: AsyncElasticsearch = Depends(get_write_es_client)) -> IngestorElkQry:
    """
    Database coupling is isolated to the query layer.
    """
    return IngestorElkQry(db)


async def get_ingestor_repo(
    elk_qry: IngestorElkQry = Depends(get_ingestor_elk_query),
) -> IngestorRepo:
    """
    Dependency function to get the repository with query layer injection.
    """
    return IngestorRepo(elk_qry)
