import json
import os
import boto3
import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

# TODO: Add tests
# TODO: integrate get_openai with the rest of the function

sm_client = boto3.client('secretsmanager')
cache_config = SecretCacheConfig()
cache = SecretCache(config=cache_config, client=sfn_client)


def get_openai_key():
    secret_name = os.environ["OPENAI_SECRET_NAME"]
    secret_value = cache.get_secret_string(secret_name)
    return json.loads(secret_value)["api_key"]

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
