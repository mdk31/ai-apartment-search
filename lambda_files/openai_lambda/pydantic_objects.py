from pydantic import BaseModel, Field


class SqlOutput(BaseModel):
    """Safe SQL output"""
    SELECT: list = Field(None)
    FROM: list = Field(None)
    JOIN: dict[list] = Field(None)
    WHERE: list = Field(None)
