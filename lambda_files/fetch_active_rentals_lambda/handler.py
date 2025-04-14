import json
import os
import boto3
import boto3
import psycopg2
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

# TODO: Add tests
# TODO: integrate get_openai with the rest of the function

sm_client = boto3.client('secretsmanager')
SECRET_NAME = os.environ["DBSECRET"]
cache = SecretCache(config=SecretCacheConfig(), client=sm_client)


def get_db_secret():
    secret_value = cache.get_secret_string(SECRET_NAME)
    return json.loads(secret_value)

def connect_to_db(creds):
    return psycopg2.connect(
        
    )

def lambda_handler(event, context):
    try:
        user_query = event.get('query', '')
        if not user_query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing 'query'"})
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
