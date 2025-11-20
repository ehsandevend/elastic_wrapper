from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from typing import Generic, TypeVar, List

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of documents")

class ElasticsearchHit(BaseModel):
    id: str = Field(..., alias="_id", description="Document ID")
    score: float = Field(..., alias="_score", description="TF-IDF (or BM25) scoring")
    source: dict = Field(..., alias="_source", description="Document source data")
    class Config:
        populate_by_name = True
        
class PaginatedResponse(BaseModel):
    meta: PaginationMeta
    results: List[dict]

class ESResponse(BaseModel):
    """
    Example for generic Elasticsearch raw result
    (if you don’t want to define a separate schema for hits)
    """
    total: int
    hits: List[ElasticsearchHit]
    
    
class ErrorDetailSchema(BaseModel):
    id: str = Field(..., description="Document ID that failed")
    reason: str = Field(..., description="Document reason that failed")


class InsertSummarySchema(BaseModel):
    inserted: int = Field(...,
                          description="Number of successfully inserted documents")
    failed: int = Field(0, description="Number of failed insertions")

class UpdateSummarySchema(BaseModel):
    updated: int = Field(...,
                          description="Number of successfully Updated documents")
    failed: int = Field(0, description="Number of failed updates")
    
class SingleInsertSchema(BaseModel):
    success: bool = Field(
        True,
        description="Whether the operation succeeded",
    )
    id: str = Field(
        ...,
        alias="_id",
        description="Document ID",
    )
    index: str = Field(
        ...,
        alias="_index",
        description="Index name",
        serialization_alias="index",
    )
    version: int = Field(
        ...,
        alias="_version",
        description="Document version",
        serialization_alias="version",
    )
    result: str = Field(
        ...,
        description="Operation result (created/updated)",
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "success": True,
                "index": "test-log-wrapper",
                "_id": "abc123",
                "version": 1,
                "result": "created",
            }
        }


class DynamicDoc(BaseModel):
    id: Optional[str] = None
    source: Dict[str, Any]

class InsertResultSchema(BaseModel):
    success: bool = Field(..., description="Whether all operations succeeded")
    summary: InsertSummarySchema | None
    errors: list[ErrorDetailSchema] | None 
    
    class Config:
            json_schema_extra = {
                "example": {
                    "success": False,
                    "errors": [
                        {
                            "_id": "OAiIcpoB_ik9gAa8yQyO",
                            "reason": "Invalid date format"
                        }
                    ]
                }
            }
            
class UpdateResultSchema(BaseModel):
    success: bool = Field(..., description="Whether all operations succeeded")
    summary: UpdateSummarySchema | None
    errors: list[ErrorDetailSchema] | None 
    
    class Config:
            json_schema_extra = {
                "example": {
                    "success": False,
                    "errors": [
                        {
                            "_id": "OAiIcpoB_ik9gAa8yQyO",
                            "reason": "Invalid date format"
                        }
                    ]
                }
            }
           
            
class JourneyQuerySchema(BaseModel):
    id: str | None = None
    title: str | None = None
    username: str | None = None
    
class UpdateInputSchema(BaseModel):
    data: Dict[str, Any]
    meta: Dict[str, Any]