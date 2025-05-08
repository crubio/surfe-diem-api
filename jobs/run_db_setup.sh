#!/bin/bash

clear

echo "Running db setup job...(db_setup.py)"

python3 tools/import_station_data.py data/stations_json_20250507T11.json

python3 tools/import_tide_stations.py data/tide_stations.json

python3 tools/import_buoy_to_tide_station.py data/buoy_to_tide_stations.json

python3 tools/import_spot_json.py data/spots_list.json

echo "Done!"
