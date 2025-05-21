import json
import os
import boto3
import boto3
import psycopg2
import requests
import time
from datetime import datetime, timedelta
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

HISTORIC_ENDPOINT = ''
YTD_ENDPOINT = ''

DB_SECRET_NAME = os.environ["DB_SECRET_NAME"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ['DB_NAME']
LIMIT_PER_REQUEST = ''
RATE_LIMIT_DELAY = ''

sm_client = boto3.client('secretsmanager')
cache = SecretCache(config=SecretCacheConfig(), client=sm_client)

def get_secrets(secret_name, key=None):
    secret_value = cache.get_secret_string(secret_name)
    secret = json.loads(secret_value)
    return secret[key] if key else secret

def connect_to_db(creds):
    return psycopg2.connect(
        host=creds["host"],
        port=int(creds["port"]),
        dbname=creds["dbname"],
        user=creds["username"],
        password=creds["password"]
    )

def fetch_all_batches(endpoint, where_clause, headers):
    all_rows = []
    offset = 0

    while True:
        params = {
            "$where": where_clause,
            "$limit": LIMIT_PER_REQUEST,
            "$offset": offset
        }
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        all_rows.extend(data)
        offset += LIMIT_PER_REQUEST
        time.sleep(RATE_LIMIT_DELAY)

    return all_rows
        

def fetch_nypd_complaints(token):
    headers = {'X-App-Token': token}
    today = datetime.today()
    current_year = today.year
    five_years_ago = (today - timedelta(days=365 * 5)).strftime('%Y-%m-%d')

    where_history = f"cmplnt_fr_dt >= '{five_years_ago}'T00:00:00"
    where_ytd = f"cmplnt_fr_dt >= '{current_year}-01-01T00:00:00'"

    history_complaints = fetch_all_batches(HISTORIC_ENDPOINT, where_history, headers)
    ytd_complaints = fetch_all_batches(YTD_ENDPOINT, where_ytd, headers)

    return history_complaints, ytd_complaints
        
def store_nypd_data(conn, complaints):
    with conn.cursor() as cursor:
        for row in complaints:
            cursor.execute(
                """
                d   
                """,
                (
                    'df'
                )
            )
    
    conn.commit()

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

