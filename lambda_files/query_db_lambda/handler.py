import json
import boto3
import psycopg2
import os
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

ALLOWED_FUNCTIONS = {

}

secrentsclient = boto3.client('secretsmanager')
cache = SecretCache(config=SecretCacheConfig(), client=secrentsclient)

def get_db_connection():
    user, password = get_db_credentials()

def get_db_credentials():
    secret_name = os.environ['DBSECRET']
    secret = json.loads(cache.get_secret_string(secret_name))
    return secret['username'], secret['password']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        action = body.get('action')

        if action == 'refresh_schema':
            refresh_schema_from_db()
        
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }



def refresh_schema_from_db():
    conn = get_db_connection()


def validate_column(col: str, from_tables: list[str], allowed_schema) -> sql.Identifier():
    if '.' in col:
        table, field = col.split('.', 1)
        if table not in allowed_schema or field not in allowed_schema[table]:
            raise ValueError(f"Undefined column: {col}")
        
        else:
            candidates = [t for t in from_tables if col in allowed_schema.get(t, set())]
            if len(candidates) != 1:
                raise ValueError(f"Ambiguous column: {col}")
            return sql.Identifier(candidates[0], col)