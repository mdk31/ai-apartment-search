import json
import os
import boto3
import boto3
import psycopg2
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

# TODO: Add tests
# TODO: integrate get_openai with the rest of the function

sm_client = boto3.client('secretsmanager')
MAX_CALLS = int(os.environ["MAX_CALLS"])
SECRET_NAME = os.environ["DBSECRET"]
STREETEASY_API_KEY_NAME = os.environ['STREETEASY_API']
cache = SecretCache(config=SecretCacheConfig(), client=sm_client)

def get_db_secret():
    secret_value = cache.get_secret_string(SECRET_NAME)
    return json.loads(secret_value)

def get_streeteasy_api_secret():
    secret_value = cache.get_secret_string(STREETEASY_API_KEY_NAME)
    return json.loads(secret_value)['x-rapidapi-key']

def connect_to_db(creds):
    return psycopg2.connect(
        host=creds["host"],
        port=int(creds["port"]),
        dbname=creds["dbname"],
        user=creds["username"],
        password=creds["password"]
    )

def fetch_active_rentals():
    rentals = []
    base_url = "https://streeteasy-api.p.rapidapi.com/rentals/search"

    areas_string = load_valid_areas()

    params = {
        'areas': areas_string,
        'limit': 500
    }

    offset = 0
    call_count = 1
    while call_count < MAX_CALLS:
        params['offset'] = offset

        response



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
