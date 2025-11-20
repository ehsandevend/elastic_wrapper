from typing import TypeVar

from pydantic import BaseModel
from apps.journey.api.v1.schemas import ESResponse, InsertResultSchema, JourneyQuerySchema, PaginatedResponse, UpdateInputSchema, UpdateResultSchema
from apps.journey.query import BaseQuery

T = TypeVar("T", bound=BaseModel)


class JourneyRepo:
    def __init__(self, query: BaseQuery):
        self.query = query

    async def get_journey_by_id(
        self, id: str
    ) -> dict:
        res = await self.query.get_by_id(id)
        return res

    async def search_journey(
        self, query_data: JourneyQuerySchema, size: int = 10
    ) -> ESResponse:
        must_filters = []
        should_queries = []
        if query_data.id:
            must_filters.append({"term": {"id.keyword": query_data.id}})

        if query_data.title:
            should_queries.append(
                {"term": {"title.keyword": {"value": query_data.title, "boost": 5}}})
            should_queries.append({
                "match": {
                    "title": {
                        "query": query_data.title,
                        "fuzziness": "AUTO"
                    }
                }
            })
        if query_data.username:
            should_queries.append(
                {"term": {"username.keyword": {"value": query_data.username, "boost": 4}}})
            should_queries.append({
                "match": {
                    "username": {
                        "query": query_data.username,
                        "fuzziness": "AUTO"
                    }
                }
            })
        es_query_body = {
            "size": size,
            "query": {
                "bool": {
                    "must": must_filters,
                    "should": should_queries
                }
            }
        }
        res = await self.query.search(es_query_body)
        return res

    async def update_journey(
        self, id: str, input: UpdateInputSchema
    ) -> UpdateResultSchema:
        res = await self.query.update(id, input)
        return res

    async def save_journey(
        self, input: dict
    ) -> InsertResultSchema:
        res = await self.query.save(input)
        return res

    async def save_journeys(
        self, inputs: list[dict]
    ) -> InsertResultSchema:
        res = await self.query.bulk_save(inputs)
        return res

    async def all_journeys(
        self,
    ) -> ESResponse:
        res = await self.query.all()
        return res

    async def all_journeys_with_pagination(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse:
        res = await self.query.all_paginated(page=page, size=size)
        return res
