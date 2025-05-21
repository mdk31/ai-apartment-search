import json
import os
import boto3
import boto3
import psycopg2
import requests
from datetime import datetime, timedelta
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from psycopg2.extensions import connection as PGConnection

# TODO: add streeteasy api key name

MAX_CALLS = int(os.environ["MAX_CALLS"])
DB_SECRET_NAME = os.environ["DB_SECRET_NAME"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ['DB_NAME']
STREETEASY_API_KEY_NAME = ''
AREA_FILE = os.path.join(os.path.dirname(__file__), 'valid_streeteasy_areas.txt')
CHUNK_SIZE = 50

# Divide max calls up
MAX_ACTIVE_CALLS = MAX_CALLS // 5
MAX_DETAIL_CALLS = MAX_CALLS - MAX_ACTIVE_CALLS

sm_client = boto3.client('secretsmanager')
cache = SecretCache(config=SecretCacheConfig(), client=sm_client)

def _ensure_active_rentals(conn: PGConnection):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_rentals (
                id TEXT PRIMARY KEY,
                url TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION
            );
        """)
    conn.commit()

def _ensure_rental_details(conn: PGConnection):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rental_details (

            );
        """)
    conn.commit()


def get_db_secret():
    secret_value = cache.get_secret_string(DB_SECRET_NAME)
    return json.loads(secret_value)

def get_streeteasy_api_secret():
    secret_value = cache.get_secret_string(STREETEASY_API_KEY_NAME)
    return json.loads(secret_value)['x-rapidapi-key']

def connect_to_db(creds):
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=creds["username"],
        password=creds["password"]
    )

def fetch_active_rentals(api_key):
    rentals = []
    base_url = "https://streeteasy-api.p.rapidapi.com/rentals/search"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "streeteasy-api.p.rapidapi.com"
    }

    area_chunks = load_valid_areas()
    call_count = 0
    for chunk in area_chunks:
        offset = 0
        while call_count < MAX_CALLS:
            params = {
                'areas': ','.join(chunk),
                'limit': 500,
                'offset': offset
            }
            try:
                response = requests.get(base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                listings = data.get('listings', [])
                if not listings:
                    print(f"[INFO] No listings returned for areas: {chunk}, offset: {offset}")
                else:
                    rentals.extend(listings)
            except Exception as e:
                print(f"[ERROR] Failed API call for areas: {chunk}, offset: {offset} — {e}")

            offset += 500
            call_count+= 1
        
    return rentals

def fetch_rental_details(api_key, rental_id):
    url = f"https://streeteasy-api.p.rapidapi.com/rentals/{rental_id}"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "streeteasy-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_existing_detail_ids(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM rental_details")
        return set(row[0] for row in cursor.fetchall())

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

def load_valid_areas(chunk_size=CHUNK_SIZE):
    with open(AREA_FILE, 'r') as file:
        all_areas = [line.strip() for line in file if line.strip()]
        return [all_areas[i:i + chunk_size] for i in range(0, len(all_areas), chunk_size)]

def store_active_rentals(conn, rentals):
    _ensure_active_rentals(conn)
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE active_rentals")
        for rental in rentals:
            cursor.execute(
                """
                INSERT INTO active_rentals (
                    id,
                    url,
                    latitude,
                    longitude
                    )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    rental['id'],
                    rental['url'],
                    rental['latitude'],
                    rental['longitude']
                )
            )
    conn.commit()
                        
def store_rental_details(conn, details):
    with conn.cursor() as cursor:
        for detail in details:
            cursor.execute(
                """
                INSERT INTO rental_details (
                    id,
                    listedAt,
                    closedAt,
                    availableFrom,
                    address,
                    price,
                    borough,
                    neighborhood,
                    zipcode,
                    propertyType,
                    sqft,
                    bedrooms,
                    bathrooms,
                    amenities,
                    builtIn,
                    images
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    detail['id'],
                    detail['listedAt'],
                    detail['closedAt'],
                    detail['availableFrom'],
                    detail['address'],
                    detail['price'],
                    detail['borough'],
                    detail['neighborhood'],
                    detail['zipcode'],
                    detail['propertyType'],
                    detail['sqft'],
                    detail['bedrooms'],
                    detail['bathrooms'],
                    json.dumps(detail['amenities']),
                    detail['builtIn'],
                    json.dumps(detail['images'])
                )
            )
    conn.commit()