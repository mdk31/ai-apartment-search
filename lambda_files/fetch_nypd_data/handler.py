import json
import os
import boto3
import boto3
import psycopg2
import requests
from datetime import datetime, timedelta
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

# TODO: Add tests
# TODO: update finish requests function
# TODO: write load areas helper

MAX_CALLS = int(os.environ["MAX_CALLS"])
SECRET_NAME = os.environ["DBSECRET"]

SODA_LIMIT = 1000
RATE_LIMIT_DELAY = 0.5

sm_client = boto3.client('secretsmanager')
cache = SecretCache(config=SecretCacheConfig(), client=sm_client)

def get_db_secret():
    secret_value = cache.get_secret_string(SECRET_NAME)
    return json.loads(secret_value)

def get_soda_api_secret():
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


def fetch_nypd_complaints(bootstrap):
    today = datetime.today()
    current_year = today.year

    # initial window
    five_years_ago = (today - timedelta(days=365 * 5)).strftime('%Y-%m-%d')
    where_clause = f"cmplnt_fr_dt >= '{five_years_ago}'T00:00:00"

    one_year_ago = (today - timedelta(days=365)).strftime('%Y-%m-%d')

    # loop through years
    while current_year >= 2010:
        start_date = f"{current_year}-01-01"
        


def lambda_handler(event, context):
    db_creds = get_db_secret()
    api_key = get_streeteasy_api_secret()
    conn = connect_to_db(db_creds)

    try:
        active_rentals = fetch_active_rentals(api_key)
        store_active_rentals(conn, active_rentals)

        existing_ids = get_existing_detail_ids(conn)
        missing = [r for r in active_rentals if r['id'] not in existing_ids]

        details = []
        for rental in missing:
            try:
                detail = fetch_rental_details(api_key, rental['id'])
                details.append(detail)
            except Exception as e:
                print(f"Error fetching details for rental {rental['id']}: {e}")
                continue

        store_rental_details(conn, details)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"{len(active_rentals)} rentals fetched, {len(details)} new details stored successfully"})
        }

    finally:
        conn.close()

