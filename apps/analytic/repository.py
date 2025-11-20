from apps.analytic.query import AnalyticElkQry


class AnalyticRepo:
    def __init__(self, elk_qry: AnalyticElkQry):
        self.elk_qry = elk_qry

    async def get_claim_flow_by_eclaim_id(self, eclaim_id):
        res = await self.elk_qry.get_claim_flow_by_eclaim_id(eclaim_id)
        return res

    async def get_claim_flow_by_document_id(self, document_id):
        res = await self.elk_qry.get_claim_flow_by_document_id(document_id)
        return res

    async def get_claim_flow_by_claim_id(self, claim_id):
        res = await self.elk_qry.get_claim_flow_by_claim_id(claim_id)
        return res
