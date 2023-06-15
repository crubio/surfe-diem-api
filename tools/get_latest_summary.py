import json
import logging
import os
import re
import sys
from datetime import datetime as dt
from enum import Enum
from urllib.request import urlopen

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

from station_ids import *

conn = psycopg2.connect(
   database=os.environ.get('DATABASE_NAME'), user=os.environ.get('DATABASE_USERNAME'), password=os.environ.get('DATABASE_PASSWORD'),
   host=os.environ.get('DATABASE_HOSTNAME'), port=os.environ.get('DATABASE_PORT')
)

# Examples for testing
# example url: https://www.ndbc.noaa.gov/data/latest_obs/46042.txt
# local_file_sample = "file:////Users/crubio/Projects/surfe-diem-api/migration_tools/46042.txt"

# maps to the table names
summary_props = {
    "timestamp": "timestamp",
    "Pres": "precipitation",
    "Seas": "wvht",
    "Wind": "wind",
    "Gust": "gust",
    "Peak Period": "peak_period",
    "Water Temp": "water_temp",
    "Swell": "swell",
    "Period": "period",
    "Direction": "direction",
    "Wind Wave": "wind_wave"
}

def main():
    timestamp = dt.now().strftime("%Y%m%dT%H")
    logging.basicConfig(filename=f'latest_summary_{timestamp}.log', filemode='w', level=logging.DEBUG)
    for id in station_ids:
        summary = get_latest_summary(id)
        import_summary(summary, id)
    conn.close()

def get_hour_int(t):
    hour = t[:2]
    return int(hour)

def format_timestamp(date_text: str):
    '''returns and iso formatted string from the expected dt format
    example: 1900 GMT 06/07/23
    '''
    try:
        date_text = date_text.split(" ")
        hour = get_hour_int(date_text[0]);
        date_parts = date_text[2].split("/")
        return dt(int(f"20{date_parts[2]}"), int(date_parts[0]), int(date_parts[1]), hour)
    except ValueError as e:
        logging.warning(f"Could not parse timestamp: {e}")
        return None

def import_summary(summary, id):
    '''Import a summary into the database'''
    if summary == None:
        logging.warning(f"no data for station id: {id}")
        logging.warning(f"check 'https://www.ndbc.noaa.gov/data/latest_obs/{id}.txt' to verify")
        return
    table_name = "locations_noaa_summary"
    fields = dict.keys(summary)
    records = list(dict.values(summary))
    cursor = conn.cursor()
    query = sql.SQL("insert into {} ({}) values ({})").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, fields)),
        sql.SQL(', ').join(sql.Placeholder() * len(fields)))

    cursor.execute(query,records)
    try:
        conn.commit()
    except:
        logging.error(f"error inserting row for id: {id}")
    
def parse_summary(summary: list, id: int, is_wind_wave = False):
    result = {}
    for index, row in enumerate(summary):
        try:
            if index == 0:
                continue
            elif len(row) <= 1:
                # timestamp row
                result['timestamp'] = format_timestamp(row[0])
            elif is_wind_wave:
                ww_key = f"ww_{summary_props[row[0]]}"
                value = row[1] or ""
                result[ww_key] = value
            else:
                key = summary_props[row[0]]
                value = row[1] or ""
                result[key] = value
        except:
            logging.warning(f"error on id: {id}, row: {row}")
    return result


def get_latest_summary(id: int):
    '''Gets the latest summary data and puts it in the database. This data is available through NOAA.'''
    logging.info(f"Running latest_summary for {id}")
    try:
        # use local file const for testing
        page = urlopen(f"https://www.ndbc.noaa.gov/data/latest_obs/{id}.txt")
        location_summary = []
        wave_summary = []
        wind_wave_summary = []
        is_wind_wave = False
        is_wave_summary = False
        location_object = {"location_id": id}
        for index, line in enumerate(page):
            # first two lines are always station name + station_id which we already have. the third line is local time which we don't need
            if index <= 2:
                continue
            
            decoded_line = line.decode('iso8859-1').rstrip()

            # if we have two parts, its a key value pair. 
            parts = re.split(':', decoded_line)

            if parts[0] == '\n' or parts[0] == '':
                continue

            # the lines following this text are a different data set we should capture
            if parts[0].__contains__("Wave Summary"):
                is_wave_summary = True
                
            if parts[0].__contains__("Wind Wave"):
                is_wind_wave = True
            
            if is_wave_summary == True:
                if is_wind_wave == True:
                    wind_wave_summary.append(parts)
                else:
                    wave_summary.append(parts)
            else:
                location_summary.append(parts)
        
        return {
            **location_object,
            **parse_summary(location_summary, id),
            **parse_summary(wave_summary, id),
            **parse_summary(wind_wave_summary, id, True)}
    except:
        logging.error(f"Could not parse station id: {id}")
        pass

if __name__ == '__main__':
    main()
