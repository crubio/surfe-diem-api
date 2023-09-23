import logging
import os
from urllib.request import urlopen
from dotenv import load_dotenv
import feedparser
from bs4 import BeautifulSoup
import sqlite3 as sql
from station_ids import *
import json

'''
Check latest observations on NOAA if we are getting errors importing data.
Files are located here: https://www.ndbc.noaa.gov/data/latest_obs/
'''

local_rss = "file:///Users/crubio/Projects/surfe-diem-api/data/latest_observation.rss"
local_xml = "file:///Users/crubio/Projects/surfe-diem-api/data/latest_observation.xml"
remote_url = "https://www.ndbc.noaa.gov/data/latest_obs/{id}.rss"

load_dotenv()

# conn = psycopg2.connect(
#    database=os.environ.get('DATABASE_NAME'), user=os.environ.get('DATABASE_USERNAME'), password=os.environ.get('DATABASE_PASSWORD'),
#    host=os.environ.get('DATABASE_HOSTNAME'), port=os.environ.get('DATABASE_PORT')
# )

database = os.environ.get('SQLITE_DB')
conn = sql.connect(database, check_same_thread=False)

rss_props = {
    "location_id": "location_id",
    "timestamp": "timestamp",
    "title": "title",
    "href": "href",
    "published": "published",
    "Wind Speed": "wind_speed",
    "Dominant Wave Period": "dominant_wave_period",
    "Dew Point": "dew_point",
    "Water Temperature": "water_temp",
    "Mean Wave Direction": "mean_wave_direction",
    "Wind Gust": "wind_gust",
    "Average Period": "average_period",
    "Location": "location",
    "Wind Direction": "wind_direction",
    "Air Temperature": "air_temp",
    "Atmospheric Pressure": "atmospheric_pressure",
    "Significant Wave Height": "significant_wave_height",
}

def main():
    logging.basicConfig(level=logging.INFO)
    station_json = []
    for station in station_ids:
        rss = get_latest_summary(station)
        if not rss:
            continue
        station_json.append(rss)
    write_to_file(json.dumps(station_json))
    # insert_from_file()
    return

def map_rss_props(rss):
    mapped_rss = {}
    for k, v in rss.items():
        if k in rss_props:
            mapped_rss[rss_props[k]] = v
    return mapped_rss

def generate_url(id):
    return remote_url.format(id=id)

def write_to_file(dump):
    with open('data/latest_observation.json', 'w') as outfile:
        outfile.write(dump)

def insert_from_file():
    with open('data/latest_observation.json') as json_file:
        data = json.load(json_file)
        for row in data:
            insert_rss(row['location_id'], row)

def insert_rss(id, rss):
    logging.info(f"Running insert_rss for {id}")
    if rss is None:
        logging.warning(f"No valid rss feed for {id}")
        return
    mapped_rss = map_rss_props(rss)
    cur = conn.cursor()
    try:
        columns_string = ','.join(mapped_rss.keys())
        values_string = ','.join('?' * len(mapped_rss.keys()))
        values = tuple(mapped_rss.values())
        cur.execute(f'''INSERT INTO locations_latest_observation({columns_string})
            VALUES({values_string})''',values)
        conn.commit()
        logging.info(f"Successfully inserted rss for {id}")
    except Exception as e:
        logging.warning(f"Could not insert rss for {id}. error: {e}")
        pass
    
def get_latest_summary(id):
    logging.info(f"Running latest_summary for {id}")
    url = generate_url(id)
    result = {}
    try:
        feed = feedparser.parse(url).entries[0]
        title = feed.title
        href = feed.links[0].href
        published = feed.published

        html = feed.description
        soup = BeautifulSoup(html, 'html.parser')
        for index, tags in enumerate(soup.find_all('strong')):
            if index == 0:
                result['timestamp'] = tags.text
            else:
                result[tags.text.strip(":")] = tags.next_sibling.strip()
        result['title'] = title
        result['href'] = href
        result['published'] = published
        result['location_id'] = id
        return result
    except Exception as e:
        logging.warning(f"Could not get latest summary for {id}. Verify {url} is valid.")
        pass

if __name__ == "__main__":
    main()