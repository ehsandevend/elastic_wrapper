from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any, Optional

from apps.analytic.api.v1.schemas import ClaimFlowSchema
from shared.enums import ModelTagChoices

class AnalyticElkQry:
    def __init__(self, db: AsyncElasticsearch):
        self.db = db
        self.index_name = "historical_claim"

    # Convenience methods for backward compatibility
    async def get_claim_flow_by_claim_id(self, claim_id: int):
        return await self.get_claim_flow(claim_id, "health_insured_claim")

    async def get_claim_flow_by_document_id(self, document_id: int):
        return await self.get_claim_flow(document_id, "health_document")

    async def get_claim_flow_by_eclaim_id(self, eclaim_id: int):
        return await self.get_claim_flow(eclaim_id, "eclaim")

    @staticmethod
    def _remove_back_to_back_duplicates(
            docs: List[Dict[str, Any]]
    ) -> List[ClaimFlowSchema]:
        if not docs:
            return []

        result = []
        # Track last state for each model_tag
        last_state_by_model = {}

        for doc in docs:
            source = doc.get("source", doc)
            model_tag = source.get("model_tag")
            state = source.get("state")

            # Get the last state for this model_tag
            last_state = last_state_by_model.get(model_tag)

            if last_state is None or state != last_state:
                data = ClaimFlowSchema(**doc).model_dump()
                result.append(data)
                last_state_by_model[model_tag] = state
            # else: skip this document (it's a back-to-back duplicate)

        return result

    async def _get_junction_doc(
        self, field_name: str, value: int
    ) -> Optional[Dict[str, Any]]:
        query = _build_term_query_by_field_and_tag(
            field_value=value,
            field_name=field_name,
            model_tag=ModelTagChoices.CLAIM_JUNCTION,
        )
        resp = await self.db.search(index=self.index_name, query=query, size=1)
        hits = resp.get("hits", {}).get("hits", [])
        if not hits:
            return None
        return hits[0]

    async def get_claim_flow(
        self, value: int, field_name: str = "health_insured_claim"
    ) -> List[ClaimFlowSchema]:
        junction = await self._get_junction_doc(field_name, value)
        if not junction:
            return []

        src = junction["_source"]
        claim_id = src.get("health_insured_claim")
        document_id = src.get("health_document")
        damage_request_id = src.get("eclaim")

        # Query 2: Get all related documents in one query
        should_clauses = []

        if claim_id:
            should_clauses.append(
                _build_term_query_by_field_and_tag(
                    claim_id, ModelTagChoices.CLAIM
                )
            )

        if document_id:
            should_clauses.append(
                _build_term_query_by_field_and_tag(
                    document_id, ModelTagChoices.DOCUMENT
                )
            )

        if damage_request_id:
            should_clauses.append(
                _build_term_query_by_field_and_tag(
                    damage_request_id, ModelTagChoices.E_DAMAGE_REQUEST
                )
            )

        if not should_clauses:
            return []

        # Single query with sorting
        query = {"bool": {"should": should_clauses, "minimum_should_match": 1}}

        resp = await self.db.search(
            index=self.index_name,
            query=query,
            sort=[{"timestamp": {"order": "asc"}}],
            size=300,
        )

        docs = resp.get("hits", {}).get("hits", [])
        return self._remove_back_to_back_duplicates(docs)

def _build_term_query_by_field_and_tag(field_value, model_tag, field_name: str = "id"):
    return {
        "bool": {
            "must": [
                {"term": {field_name: field_value}},
                {"term": {"model_tag.keyword": model_tag}},
            ]
        }
    }
