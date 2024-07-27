import logging
import os

import dotenv
import pandas as pd
from sqlalchemy import Table, Column, String, Integer, Float, TIMESTAMP
from sqlalchemy.exc import SQLAlchemyError

dotenv.load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_TABLE_OCEAN_HISTORICAL = os.getenv('DB_TABLE_OCEAN_HISTORICAL')
DB_TABLE_MET_HISTORICAL = os.getenv('DB_TABLE_MET_HISTORICAL')
BASE_URI = "https://mw.buoybay.noaa.gov/api/v1/"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def infer_sqlalchemy_type(dtype):
    """Map to SQLAlchemy types"""
    dtype_mapping = {
        'int': Integer,
        'float': Float,
        'decimal': Float,
        'datetime': TIMESTAMP,
        'object': String(255)
    }
    for key, sql_type in dtype_mapping.items():
        if key in dtype.name:
            return sql_type
    return String(255)


def create_table(metadata, df, table_name):
    """Create the table schema based on DataFrame dtypes"""
    columns = [Column(name, infer_sqlalchemy_type(dtype)) for name, dtype in df.dtypes.items()]
    table = Table(table_name, metadata, *columns)
    logging.info(f"Table schema for '{table_name}' successfully created.")
    return table


def remove_duplicates(df, table, engine, time_col='time_utc'):
    """Remove duplicates for updating new data in the DB"""
    try:
        df = df.reset_index(drop=True)
        print(df.index)
        with engine.connect() as connection:
            existing_data = pd.read_sql_table(table.name, connection)
            merged_df = pd.concat([existing_data, df]).drop_duplicates(subset=[time_col], keep='last',
                                                                       ignore_index=True)
            new_data = merged_df[~merged_df.index.isin(existing_data.index)]
            return new_data
    except SQLAlchemyError as e:
        logging.error(f"Error querying the database for duplicates: {e}")
        raise
