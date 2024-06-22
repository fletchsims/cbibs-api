import pandas as pd
import os
from dotenv import load_dotenv
import collections
import requests
import re

load_dotenv()

CB_STATIONS = [
    ("ANNAPOLIS", "AN"),
    ("FIRST_LANDING", "FL"),
    ("GOOSES_REEF", "GR"),
    ("JAMESTOWN", "J"),
    ("NORFOLK", "N"),
    ("POTOMAC", "PL"),
    ("SUSQUEHANNA", "S"),
    ("PATAPSCO", "SN"),
    ("STINGRAY_POINT", "SP"),
    ("UPPER_POTOMAC", "UP"),
    ("YORK_SPLIT", "YS"),
]
station_ids = {station: code for station, code in CB_STATIONS}
OCEAN_FILES = []
MET_FILES = []
for i in os.listdir("/Users/fletcherbsims/Downloads/buoybay-reports-45388/"):
    if re.search("(MET)", i):
        MET_FILES.append(i)
    elif re.search("(OCEAN)", i):
        OCEAN_FILES.append(i)
    else:
        None

# Let's just load in the Annapolis buoy data
an_met = pd.read_csv(os.getenv('PATH_TO_MET'), skiprows=lambda x: x in [1, 2])
an_ocean = pd.read_csv(os.getenv('PATH_TO_OCEAN'), skiprows=lambda x: x in [1, 2])

# Let's check for null values
# print(an_ocean.isnull().sum())
# print(an_met.isnull().sum())
print(an_met.count())
print(an_ocean.count())