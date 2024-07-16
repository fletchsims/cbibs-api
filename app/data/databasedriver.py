import dotenv
from sqlalchemy import create_engine

from settings import DB_NAME, DB_HOST, DB_PORT, DB_PASSWORD, DB_USER

# Load env variables
dotenv.load_dotenv()


class DatabaseDriver:
    def __init__(self):
        self.db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    def db_create_engine(self):
        create_engine(self.db_url)