import json
from station_ids import *
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime as dt

BUOY_URL = "https://www.ndbc.noaa.gov/station_page.php?station="

# TODO: station page HTML isn't consistent enough to get accurate scrapes. Fix later.
def get_stations():
    stations = []
    for id in station_ids:
        data = {}
        page = urlopen(f"{BUOY_URL}{id}")
        html_bytes = page.read()
        html = html_bytes.decode()
        soup = BeautifulSoup(html, 'html.parser')

        # tags from inspecting the html
        title_tag = "#contents h1"
        station_meta_tag = "#stn_info #stn_metadata > p"

        station_title = soup.css.select(title_tag)[0].text
        station_meta = soup.css.select(station_meta_tag)[0].text.split("\n")
        station_meta = list(filter(None, station_meta))

        data["location_id"] = str(id)
        data["name"] = station_title
        data["url"] = f"{BUOY_URL}{id}"
        data["description"] = station_meta[1] or ''
        data["location"] = station_meta[2] or '' 
        data["elevation"] = station_meta[3] or ''

        stations.append(dict(data))
        data.clear
    
    timestamp = dt.now().strftime("%Y%m%dT%H")
    filename = f"stations_json_{timestamp}"

    with open(f'{filename}.json', 'w') as outfile:
        json.dump(stations, outfile,indent=4)
    return

if __name__ == '__main__':
    get_stations()