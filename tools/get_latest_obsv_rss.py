import logging
import os
from urllib.request import urlopen
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import feedparser
from bs4 import BeautifulSoup
from station_ids import *

load_dotenv()

local_rss = "file:///Users/crubio/Projects/surfe-diem-api/data/latest_observation.rss"
local_xml = "file:///Users/crubio/Projects/surfe-diem-api/data/latest_observation.xml"
remote_url = "https://www.ndbc.noaa.gov/data/latest_obs/{id}.rss"

conn = psycopg2.connect(
   database=os.environ.get('DATABASE_NAME'), user=os.environ.get('DATABASE_USERNAME'), password=os.environ.get('DATABASE_PASSWORD'),
   host=os.environ.get('DATABASE_HOSTNAME'), port=os.environ.get('DATABASE_PORT')
)

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
    logging.info("Starting get_latest_rss.py")
    for station in station_ids:
        rss = get_latest_summary(station)
        if not rss:
            continue
        insert_rss(station, rss)
    conn.close()
    logging.info("Finished get_latest_rss.py")
    return

def map_rss_props(rss):
    mapped_rss = {}
    for k, v in rss.items():
        if k in rss_props:
            mapped_rss[rss_props[k]] = v
    return mapped_rss

def generate_url(id):
    return remote_url.format(id=id)

def insert_rss(id, rss):
    logging.info(f"Running insert_rss for {id}")
    if rss is None:
        logging.warning(f"No valid rss feed for {id}")
        return
    table_name = "locations_latest_observation"
    mapped_rss = map_rss_props(rss)
    cur = conn.cursor()
    try:
        cur.execute(sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(',').join(map(sql.Identifier, mapped_rss.keys())),
            sql.SQL(',').join(map(sql.Placeholder, mapped_rss.keys()))
        ), mapped_rss)
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
        logging.warning(f"Could not get latest summary for {id}. Error: {e}")
        pass

if __name__ == "__main__":
    main()