#!/bin/bash

clear

echo "Running db setup job...(db_setup.py)"

python3 tools/import_station_data.py data/stations_json_20230913T14.json

python3 tools/import_tide_stations.py data/tide_stations.json

python3 tools/import_buoy_to_tide_station.py data/buoy_to_tide_stations.json

echo "Done!"
