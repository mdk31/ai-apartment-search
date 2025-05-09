from pydantic import BaseModel, Field
from typing import Literal


class JoinCondition(BaseModel):
    name: Literal["ST_DWithin"]
    args: list[str | int | float]


class Join(BaseModel):
    type: Literal["inner", "left"]
    table: Literal["nypd_complaints"]
    on: JoinCondition


class WhereClause(BaseModel):
    column: str
    operator: Literal["=", "!=", "<", "<=", ">", ">="]
    value: str | int | float


class HavingClause(BaseModel):
    aggregate: Literal["COUNT", "AVG", "SUM", "MAX", "MIN"]
    column: str
    operator: Literal["=", "!=", "<", "<=", ">", ">="]
    value: int | float


class SqlOutput(BaseModel):
    """Safe SQL Output"""
    SELECT: list[str]
    FROM: list[Literal["listings"]]
    JOINS: list[Join] = Field(None)
    WHERE: list[WhereClause] = Field(None)
    GROUPBY: list[str] = Field(None)
    HAVING: list[HavingClause] = Field(None)
