from pydantic import BaseModel, Field


class ClaimFlowSchema(BaseModel):
    id: str = Field(
        ...,
        alias="_id",
        description="Document ID",
    )
    index: str = Field(
        ...,
        alias="_index",
        description="Index name",
    )
    source: dict = Field(
        alias="_source",
        description="Document source",
    )
