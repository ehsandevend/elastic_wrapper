from apps.ingestor.query import IngestorElkQry
from .api.v1.schemas import BulkInsertSchema, SingleInsertSchema


class IngestorRepo:
    def __init__(self, elk_qry: IngestorElkQry):
        self.elk_qry = elk_qry

    async def insert_doc(
        self, log_data: dict, index_name: str
    ) -> SingleInsertSchema:
        res = await self.elk_qry.insert_doc(log_data, index_name)
        return res

    async def bulk_insert_docs(
        self, logs_data: list[dict], index_name: str
    ) -> BulkInsertSchema:
        res = await self.elk_qry.bulk_insert_docs(logs_data, index_name)
        return res
