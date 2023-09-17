Importing data from JSON files

This can be done on the prod server before deploys. I usuaally run the "get_something.py" scripts on my local machine, then copy the JSON files to the prod server.

Run the following command to import data from JSON files:

```bash
# import buoy station data
$ python3 tools/import_station_data.py data/stations_json_20230913T14.json

# import tide station data
$ python3 tools/import_tide_station_data.py data/tide_stations.json

# import tide to buoy data
$ python3 tools/import_buoy_to_tide_station.py data/buoy_to_tide_stations.json