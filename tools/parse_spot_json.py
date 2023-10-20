import sys
import os
import json
import sqlite3 as sql
from dotenv import load_dotenv

load_dotenv()

# sqlite connection string
database = os.environ.get('SQLITE_DB')
conn = sql.connect(database, check_same_thread=False)

def main(argv):
    print(f"parse_spot_json.py - {sys.argv[1]}")
    parse_json(argv)

def parse_json(json_file):
    if not json_file:
        raise Exception('No json file specified')
    cursor = conn.cursor()
    with open(json_file) as data_file:
        data = json.load(data_file)
        for row in data:
            try:
                cursor.execute('''INSERT INTO spot_location(name, latitude, longitude, timezone, subregion_name)
                    VALUES(?,?,?,?,?)''',
                    (
                        row['name'], row['lat'], row['lon'], row['timezone'], row['subregion']['name']
                    ))
            except Exception as error:
                print(f"Error inserting row: {error}")
                conn.commit()
                continue
            conn.commit()
    conn.close()

if __name__ == "__main__":
    main(sys.argv[1])