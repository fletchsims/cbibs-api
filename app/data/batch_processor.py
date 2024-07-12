import glob
import logging
import os

import dotenv
import pandas as pd
from sqlalchemy import create_engine, Table, Column, String, MetaData, Integer, Float
from sqlalchemy.exc import SQLAlchemyError

from settings import DB_NAME, DB_HOST, DB_PORT, DB_PASSWORD, DB_TABLE_OCEAN, DB_USER, DB_TABLE_MET

# Load env variables
dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

met_column_alias = {
    'Time (UTC)': 'time_utc',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Air Temperature QC': 'air_temperature_qc',
    'Air Temperature': 'air_temperature',
    'Air pressure QC': 'air_pressure_qc',
    'Air pressure': 'air_pressure',
    'Humidity QC': 'humidity_qc',
    'Humidity': 'humidity',
    'Wind speed QC': 'wind_speed_qc',
    'Wind speed': 'wind_speed',
    'Wind Direction QC': 'wind_direction_qc',
    'Wind Direction': 'wind_direction',

}
ocean_column_alias = {
    'Time (UTC)': 'time_utc',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Temperature QC': 'temperature_qc',
    'Temperature': 'temperature',
    'Salinity QC': 'salinity_qc',
    'Salinity': 'salinity',
    'Chlorophyll QC': 'chlorophyll_qc',
    'Chlorophyll': 'chlorophyll',
    'Turbidity QC': 'turbidity_qc',
    'Turbidity': 'turbidity',
    'Oxygen QC': 'oxygen_qc',
    'Oxygen': 'oxygen',
    'Waves QC': 'waves_qc',
    'Significant wave height': 'significant_wave_height',
    'Wave from direction': 'wave_from_direction',
    'Wave period': 'wave_period',
    'North surface currents': 'north_surface_currents',
    'East surface currents': 'east_surface_currents'
}


def infer_sqlalchemy_type(dtype):
    """Map to SQLAlchemy types"""
    dtype_mapping = {
        'int': Integer,
        'float': Float,
        'decimal': Float,
        'object': String(255)
    }
    for key, sql_type in dtype_mapping.items():
        if key in dtype.name:
            return sql_type
    return String(255)


def load_and_process_csv(file_path, col_alias=None):
    """Load and process CSV file"""
    try:
        all_files = glob.glob(os.path.join(file_path, "*.csv"))
        data = pd.concat(
            (pd.read_csv(f, skiprows=lambda x: x in [1, 2]).rename(columns=col_alias) for f in all_files),
            ignore_index=True)
        logging.info("CSV file loaded successfully.")
        return data
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except pd.errors.ParserError as e:
        logging.error(f"Error parsing CSV file: {3}")
        raise


def create_table(metadata, df, table_name):
    """Create the table schema based on DataFrame dtypes"""
    columns = [Column(name, infer_sqlalchemy_type(dtype)) for name, dtype in df.dtypes.items()]
    table = Table(table_name, metadata, *columns)
    logging.info(f"Table schema for '{table_name}' successfully created.")
    return table


def etl(file_path_var, schema, db_table_name):
    """ Main function to execute ETL process """
    logging.info(f"Running ETL for '{db_table_name}'")
    try:
        fp = os.getenv(file_path_var)
        if not fp:
            logging.error(f"Environmental variable not set: '{file_path_var}'")
        df = load_and_process_csv(fp, schema)

        metadata = MetaData()
        table_name = f'an_{db_table_name}'
        table = create_table(metadata, df, table_name)

        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        table.create(engine)
        df.to_sql(table_name, engine, schema='public', index=False, if_exists='append')
        logging.info(f"Data inserted successfully for '{db_table_name}'.")
    except SQLAlchemyError as e:
        logging.error(f"SQLAlchemy error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise


if __name__ == '__main__':
    etl('PATH_TO_OCEAN', ocean_column_alias, DB_TABLE_OCEAN)
    etl('PATH_TO_MET', met_column_alias, DB_TABLE_MET)
