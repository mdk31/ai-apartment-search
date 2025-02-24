import boto3
import requests
import pandas as pd
import os
import json
import psycopg2
from sqlalchemy import create_engine, text

# Constants
API_URL = "https://streeteasy-api.p.rapidapi.com/rentals/search"
HEADERS = {
    "x-rapidapi-host": "streeteasy-api.p.rapidapi.com",
    "x-rapidapi-key": os.getenv("RAPID_API_KEY")
}
PARAMS = {
    "limit": 500
}

# AWS Config
AWS_REGION = "us-east-1"
SECRET_NAME = "DBSecret"  # Use the secret name from CDK output

# Fetch database credentials from Secrets Manager
def get_db_credentials():
    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=AWS_REGION)
    secret = client.get_secret_value(SecretId=SECRET_NAME)
    credentials = json.loads(secret["SecretString"])
    return credentials["username"], credentials["password"], credentials.get("host", None)

DB_USER, DB_PASS, DB_HOST = get_db_credentials()
DB_NAME = "nyc_rentals"
DB_PORT = "5432"

# Database Connection
DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URI)

def create_table():
    """Creates the rentals table in Aurora PostgreSQL."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rentals (
                id SERIAL PRIMARY KEY,
                address VARCHAR(255),
                price INT,
                beds INT,
                baths INT,
                area VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("Table 'rentals' created (if it did not exist).")

def fetch_rentals():
    """Fetches all rental listings from the API with pagination."""
    rentals = []
    page = 1
    while True:
        PARAMS["page"] = page
        response = requests.get(API_URL, headers=HEADERS, params=PARAMS)
        if response.status_code != 200:
            print(f"Error fetching data: {response.text}")
            break
        
        data = response.json()
        listings = data.get("listings", [])
        if not listings:
            break  # No more data
        
        rentals.extend(listings)
        page += 1
    
    return pd.DataFrame(rentals)

def insert_rentals_to_db(df):
    """Inserts rental data into the Aurora database."""
    if df.empty:
        print("No rental data to insert.")
        return

    with engine.connect() as conn:
        df.to_sql("rentals", conn, if_exists="append", index=False)
        print(f"Inserted {len(df)} records into rentals.")

if __name__ == "__main__":
    create_table()
    df = fetch_rentals()
    insert_rentals_to_db(df)
