import json
import boto3
import psycopg2
import os
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from psycopg2.extras import RealDictCursor

client = boto3.client('secretsmanager')
cache = SecretCache(config=SecretCacheConfig(), client=client)

def get_db_credentials():
    secret_name = os.environ['DBSECRET']
    secret = json.loads(cache.get_secret_string(secret_name))
    return secret['username'], secret['password']

def lambda_handler(event, context):
    try:
        sql = event.get('sql')
        if not sql:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing SQL"})
            }
        user, password = get_db_credentials()
        host = os.environ['DB_HOST']
        dbname = os.environ['DB_NAME']

        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=5
        )

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
