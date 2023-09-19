import logging
import sys
import os
import psycopg2
import json
import sqlite3 as sql
from dotenv import load_dotenv

# load_dotenv()

# conn = psycopg2.connect(
#    database=os.environ.get('DATABASE_NAME'), user=os.environ.get('DATABASE_USERNAME'), password=os.environ.get('DATABASE_PASSWORD'),
#    host=os.environ.get('DATABASE_HOSTNAME'), port=os.environ.get('DATABASE_PORT')
# )

# from sqlalchemy import create_engine - this is a working example of how to connect to the database
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# sqlite connection string
database = 'surfe-diem-api.db'
conn = sql.connect(database, check_same_thread=False)

def main(json_data_file):
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting import_tide_stations.py")
    import_tide_stations(json_data_file)
    logging.info("Finished import_tide_stations.py")

def import_tide_stations(json_data_file):
    if not json_data_file:
        raise Exception('No json file specified')
    cursor = conn.cursor()
    with open(json_data_file) as data_file:
        data = json.load(data_file)
        for row in data:
            try:
                cursor.execute('''INSERT INTO tide_stations(station_id, station_name, latitude, longitude)
                    VALUES(?,?,?,?)''',
                    (
                        row['stationId'], row['stationName'], row['latitude'], row['longitude']
                    ))
            except Exception as error:
                print(f"Error inserting row: {error}")
                conn.commit()
                continue
        conn.commit()
    conn.close()
    logging.info("Finished import_tide_stations.py")
    return True

if __name__ == '__main__':
    main(sys.argv[1])