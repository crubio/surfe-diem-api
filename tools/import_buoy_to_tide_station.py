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

def import_tide_stations(json_data_file):
    if not json_data_file:
        raise Exception('No json file specified')
    cursor = conn.cursor()
    with open(json_data_file) as data_file:
        data = json.load(data_file)
        for row in data:
            try:
                cursor.execute('''INSERT INTO tide_station_buoy_location(station_id, location_id)
                    VALUES(?,?)''',
                    (
                        row['station_id'], row['location_id']
                    ))
            except Exception as error:
                print(f"Error inserting row: {error}")
                conn.commit()
                continue
        conn.commit()
    conn.close()
    return True

if __name__ == '__main__':
    import_tide_stations(sys.argv[1])