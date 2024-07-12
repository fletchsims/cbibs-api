import os

import dotenv

dotenv.load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_TABLE_OCEAN = os.getenv('DB_TABLE_OCEAN')
DB_TABLE_MET = os.getenv('DB_TABLE_MET')
BASE_URI = "https://mw.buoybay.noaa.gov/api/v1/"
