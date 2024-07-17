import json
import os

import requests
from dotenv import load_dotenv
from sqlalchemy import Column, Float, String, TIMESTAMP, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.data.databasedriver import DatabaseDriver
from app.data.settings import DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_USER

# Load env variables
load_dotenv()

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


def parse_json(data):
    result = {}
    for key, value in data.items():
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


# station = StationSearch(os.getenv('CBIBS_API_KEY'), 'AN')


data = etl_station_data(json.loads(sample))
tmp = parse_json(json.loads(sample))
print(data)

station_data = StationData(
    station_short_name=data.get('station_short_name'),
    station_long_name=data.get('station_long_name'),
    op_state=data.get('op_state'),
    time_utc=data.get('time_utc'),
    air_pressure=data.get('air_pressure'),
    air_temperature=data.get('air_temperature'),
    current_average_speed=data.get('current_average_speed'),
    current_average_direction=data.get('current_average_direction'),
    latitude=data.get('latitude'),
    longitude=data.get('longitude'),
    sea_surface_wave_from_direction=data.get('sea_surface_wave_from_direction'),
    sea_surface_maximum_wave_height=data.get('sea_surface_maximum_wave_height'),
    sea_surface_wave_significant_height=data.get('sea_surface_wave_significant_height'),
    sea_surface_wind_wave_period=data.get('sea_surface_wind_wave_period'),
    sea_water_salinity=data.get('sea_water_salinity'),
    sea_water_temperature=data.get('sea_water_temperature'),
    wind_from_direction=data.get('wind_from_direction'),
    wind_speed=data.get('wind_speed'),
    wind_speed_of_gust=data.get('wind_speed_of_gust'),
    seanettle_prob=data.get('seanettle_prob'),
    wind_chill=data.get('wind_chill'),
    battery_volts=data.get('battery_volts'),
    solar_panel_charge_current=data.get('solar_panel_charge_current'),
    compass_heading=data.get('compass_heading'),
    compass_pitch=data.get('compass_pitch'),
    compass_roll=data.get('compass_roll')
)


db = DatabaseDriver
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=True)
# create our class
Session = sessionmaker(bind=engine)
# instantiate it
session = Session()

# then we can use it
session.add(station_data)


