from pydantic import BaseModel, Field
from typing import List, Union

class JoinCondition(BaseModel):
    name: str 
    args: List[Union[str, int, float]]

class Join(BaseModel)

class SqlOutput(BaseModel):
    """Safe SQL output"""
    SELECT: list = Field(None)
    FROM: list = Field(None)
    JOIN: dict[list] = Field(None)
    WHERE: list = Field(None)
