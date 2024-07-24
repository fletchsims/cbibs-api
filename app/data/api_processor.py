import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import Column, Float, String, TIMESTAMP, create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base

from app.data.batch_processor import create_table, remove_duplicates
from app.data.databasedriver import DatabaseDriver
from app.data.settings import DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_USER

# Load env variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Base = declarative_base()


class StationData(Base):
    __tablename__ = "event_cbibs"
    station_short_name = Column(String, primary_key=True)
    station_long_name = Column(String)
    op_state = Column(String)
    time_utc = Column(TIMESTAMP)
    air_pressure = Column(Float)
    air_temperature = Column(Float)
    current_average_speed = Column(Float)
    current_average_direction = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    sea_surface_wave_from_direction = Column(Float)
    sea_surface_maximum_wave_height = Column(Float)
    sea_surface_wave_significant_height = Column(Float)
    sea_surface_wind_wave_period = Column(Float)
    sea_water_salinity = Column(Float)
    sea_water_temperature = Column(Float)
    wind_from_direction = Column(Float)
    wind_speed = Column(Float)
    wind_speed_of_gust = Column(Float)
    seanettle_prob = Column(Float)
    wind_chill = Column(Float)
    battery_volts = Column(Float)
    solar_panel_charge_current = Column(Float)
    compass_heading = Column(Float)
    compass_pitch = Column(Float)
    compass_roll = Column(Float)


class StationSearch:
    def __init__(self, key: str, station: str = None):
        self.base_url = "https://mw.buoybay.noaa.gov/api/v1/"
        self.station = station
        self.key = key

    def grab_station_data(self):
        if not self.station:
            raise ValueError("Station ID must be provided")
        try:
            response = requests.get(f"{self.base_url}json/station/{self.station}/?key={self.key}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def grab_all_station_data(self):
        try:
            response = requests.get(f"{self.base_url}json/station?key={self.key}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None


with open(os.getenv('SAMPLE_JSON_PATH')) as sample_data:
    sample = sample_data.read()


def parse_json(json_data):
    result = {}
    for key, value in json_data.items():
        if isinstance(value, dict):
            result[key] = parse_json(value)
        else:
            result[key] = value
    return result


def etl_station_data(data):
    station_short_name = [station['stationShortName'] for station in data['stations']]
    station_long_name = [station['stationLongName'] for station in data['stations']]
    station_op_state = [station['opState'] for station in data['stations']]
    station_keys = ['station_short_name', 'station_long_name', 'op_state', 'time_utc']
    station_keys += [
        variable['actualName']
        for station in data['stations']
        for variable in station['variable']
    ]
    measurements = [
        msr['value']
        for station in data['stations']
        for variable in station['variable']
        for msr in variable['measurements']
    ]
    time_utc = list({
        msr['time']
        for station in data['stations']
        for variable in station['variable']
        for msr in variable['measurements']
    })
    measurements.insert(0, time_utc[0])
    measurements.insert(0, station_op_state[0])
    measurements.insert(0, station_long_name[0])
    measurements.insert(0, station_short_name[0])
    return dict(zip(station_keys, measurements))


def main(table_name, station):
    station = StationSearch(os.getenv('CBIBS_API_KEY'), station)
    df = pd.DataFrame.from_dict([etl_station_data(parse_json(station.grab_station_data()))])
    try:
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=True)
    except SQLAlchemyError as e:
        logging.error(f"Error creating engine: {e}")
        raise
    metadata = MetaData()
    try:
        if not engine.dialect.has_table(engine.connect(), table_name):
            table = create_table(metadata, df, table_name)
            table.create(engine)
        else:
            table = Table(table_name, metadata, autoload_with=engine)

        data = remove_duplicates(df, table, engine)

        if not data.empty:
            data.to_sql(table_name, engine, schema='public', index=False, if_exists='append')
            logging.info(f"Data inserted successfully for '{table_name}'. Inserted {len(data)} rows.")
        else:
            logging.info(f"No new data to insert into '{table_name}'.")
    except SQLAlchemyError as e:
        logging.error(f"SQLAlchemy error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise


if __name__ == '__main__':
    db = DatabaseDriver
    main('event_cbibs', 'AN')
