import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class StationSearch:
    def __init__(self, key: str, station: str = None):
        self._base_url = "https://mw.buoybay.noaa.gov/api/v1/"
        self.station = station
        self.key = key

    def grab_station_data(self):
        if not self.station:
            raise ValueError("Station ID must be provided")
        try:
            response = requests.get(f"{self._base_url}json/station/{self.station}/?key={self.key}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def grab_all_station_data(self):
        try:
            response = requests.get(f"{self._base_url}json/station?key={self.key}")
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


def parse_station_data(data):
    report_name = [
        variable['actualName']
        for station in data['stations']
        for variable in station['variable']
    ]
    report_name.insert(0, 'time_utc')
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
    return dict(zip(report_name, measurements))


# station = StationSearch(os.getenv('CBIBS_API_KEY'), 'AN')
# tmp = parse_json(station.grab_station_data())

tmp = parse_json(json.loads(sample))
print(tmp)
station_short_name = [station['stationShortName'] for station in tmp['stations']]
station_long_name = [station['stationLongName'] for station in tmp['stations']]
op_state = [station['opState'] for station in tmp['stations']]

print(station_short_name)
print(station_long_name)
print(op_state)
