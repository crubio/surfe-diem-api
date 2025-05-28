#!/bin/bash

clear

echo "Running db setup job...(db_setup.py)"

python3 tools/import_station_data.py data/stations_json_*.json

python3 tools/import_tide_stations.py data/tide_stations.json

python3 tools/import_spot_json.py data/spots_list.json

echo "Done!"
