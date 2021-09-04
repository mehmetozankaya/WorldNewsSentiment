from dotenv import load_dotenv
from pathlib import Path  # python3 only
import os
from pymongo import MongoClient

# set path to env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Mongo:
    """Create MongoDB Connections from .env file"""

    # Load in enviornemnt variables
    client = MongoClient(os.getenv('CONN_STRING'),tls=True,tlsAllowInvalidCertificates=True)
    db = client.get_database(os.getenv('DB_NAME'))
    nyTimesCol = db[os.getenv('NYTIMES_COL')]
    nyWcCol = db[os.getenv('NYTIMES_WC')]
    cbsNewsCol = db[os.getenv('CBSNEWS_COL')]
    cbsWcCol = db[os.getenv('CBSNEWS_WC')]
