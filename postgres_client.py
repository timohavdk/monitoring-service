import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")

postgres_client = psycopg2.connect(
    dbname=db,
    user=user,
    password=password,
    host=host,
    port=port
)

postgres_client.autocommit = True
