import pytest
import psycopg2
from psycopg2 import sql
from unittest.mock import patch, MagicMock
from lambda_files.query_db_lambda.handler import build_function_call, build_safe_sql
import json
import pdb

@pytest.fixture
def allowed_schema():
    return {
        "users": {"id", "name", "age", "location"},
        "profiles": {"user_id", "bio", "age"},
        "places": {"lat", "lng"}
    }

def test_basic_select_single_table(allowed_schema):
    query_json = {
        "select": ["users.id", "users.name"],
        "from": ["users"]
    }
    query, params = build_safe_sql(query_json, allowed_schema)
    assert isinstance(query, sql.Composed)
    assert params == []

def test_select_with_where_clause(allowed_schema):
    query_json = {
        "select": ["users.id"],
        "from": ["users"],
        "where": {
            "users.age": {"gte": 18, "lt": 30}
        }
    }
    query, params = build_safe_sql(query_json, allowed_schema)
    assert isinstance(query, sql.Composed)
    assert params == [18, 30]

def test_invalid_operator_in_where(allowed_schema):
    query_json = {
        "select": ["users.id"],
        "from": ["users"],
        "where": {
            "users.age": {"foobar": 99}
        }
    }
    with pytest.raises(ValueError, match="Unsupported operator"):
        build_safe_sql(query_json, allowed_schema)


