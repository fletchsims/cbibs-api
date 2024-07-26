import dotenv
import pandas as pd
from sqlalchemy import create_engine

# Load env variables
dotenv.load_dotenv()


class DatabaseDriver:
    def __init__(self, db_user, db_password, db_host, db_port, db_name):
        self.db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        self.engine = create_engine(self.db_url)

    def load_db_table(self, table_name):
        with self.engine.connect() as connection:
            return pd.read_sql_table(table_name, con=connection)

    def execute_query(self, query):
        with self.engine.connect() as connection:
            return pd.read_sql_query(query, con=connection)
