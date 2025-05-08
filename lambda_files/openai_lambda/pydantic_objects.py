from pydantic import BaseModel, Field
from typing import List, Union, Literal

class JoinCondition(BaseModel):
    name: str 
    args: List[Union[str, int, float]]

class Join(BaseModel):
    kind: Literal['inner', 'left']
    table: Literal['nypd_complaints']
    on: JoinCondition

class WhereClause(BaseModel):
    column: str
    operator: Literal['=', '>', '<', '<=', '>=', '!=']
    value: Union[str, float, int]

class HavingCluase(BaseModel)

class SqlOutput(BaseModel):
    """Safe SQL output"""
    SELECT: list = Field(None)
    FROM: list = Field(None)
    JOIN: dict[list] = Field(None)
    WHERE: list = Field(None)
