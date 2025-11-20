from pydantic import BaseModel, Field
from typing import List, Optional


class ErrorDetailSchema(BaseModel):
    id: Optional[str] = Field(None, description="Document ID that failed")
    reason: str = Field(..., description="Error reason")


class InsertSummarySchema(BaseModel):
    inserted: int = Field(..., description="Number of successfully inserted documents")
    failed: int = Field(0, description="Number of failed insertions")


class BulkInsertSchema(BaseModel):
    success: bool = Field(..., description="Whether all operations succeeded")
    summary: InsertSummarySchema
    errors: List[ErrorDetailSchema] = Field(
        default_factory=list, description="List of errors if any occurred"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "summary": {"inserted": 100, "failed": 0},
                "errors": [],
            }
        }


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
