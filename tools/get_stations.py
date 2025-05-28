import json
# from station_ids import *
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime as dt

BUOY_URL = "https://www.ndbc.noaa.gov/station_page.php?station="
STATION_IDS_URL = "https://www.ndbc.noaa.gov/to_station.shtml"

def parse_station_ids(ids):
    buoys = []
    for id in ids:
        if id.startswith('4'):
            buoys.append(id)
    return buoys

def get_weight(station_id):
    '''returns the weight of a station id'''
    if station_id.startswith('46'): # west coast north america
        return 10
    elif station_id.startswith('44'): #east coast north america
        return 5
    elif station_id.startswith('42'): #east coast north america
        return 5
    elif station_id.startswith('41'): #east coast north america
        return 5
    else:
        return None

def get_station_ids(url) -> set: 
    '''scrapes the NDBC website for station ids'''
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode()
    soup = BeautifulSoup(html, 'html.parser')
    station_ids = []
    station_list = soup("div", class_="station-list")

    for row in station_list:
        for link in row.find_all("a"):
            station_id = link.get('href').split('=')[1]
            station_ids.append(station_id)
    # remove duplicates
    station_ids = list(set(station_ids))
    return station_ids

def get_stations():    
    stations = []
    station_ids = parse_station_ids(get_station_ids(STATION_IDS_URL))
    # station_ids = get_station_ids(STATION_IDS_URL)
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

        station_weight = get_weight(id)
        if station_weight is None:
            station_weight = 0

        try:
            if not station_meta[2][0].isdigit():
                print("Skipping station %s, invalid location: %s", id, station_meta[2])
                continue  # skip if location is not a valid coordinate

            data["location_id"] = str(id)
            data["name"] = station_title
            data["url"] = f"{BUOY_URL}{id}"
            data["description"] = station_meta[1] or ''
            data["location"] = station_meta[2] or '' 
            data["elevation"] = station_meta[3] or ''
            data["weight"] = station_weight
        except:
            print(f"Error parsing station {id}, skipping...")
            continue


        stations.append(dict(data))
        data.clear
    
    timestamp = dt.now().strftime("%Y%m%dT%H")
    filename = f"stations_json_{timestamp}"

    with open(f'{filename}.json', 'w') as outfile:
        json.dump(stations, outfile,indent=4)
    return

if __name__ == '__main__':
    get_stations()