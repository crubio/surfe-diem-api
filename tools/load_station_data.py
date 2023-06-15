import sys
import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

# conn = psycopg2.connect(
#    database=os.environ.get('DATABASE_NAME'), user=os.environ.get('DATABASE_USERNAME'), password=os.environ.get('DATABASE_PASSWORD'),
#    host=os.environ.get('DATABASE_HOSTNAME'), port=os.environ.get('DATABASE_PORT')
# )
conn = psycopg2.connect(database_url=os.environ.get('DATABASE_URL'))

# from sqlalchemy import create_engine - this is a working example of how to connect to the database
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

def import_locations(json_data_file):
    '''runs the import from our json file'''
    if not json_data_file:
        raise Exception('No json file specified')
    cursor = conn.cursor()
    with open(json_data_file) as data_file:
        data = json.load(data_file)
        for row in data:
            cursor.execute('''INSERT INTO locations(location_id, name, url, active, description, elevation, depth, location)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    row['location_id'], row['name'], row['url'], True, row['description'], row['elevation'], row['depth'], row['location']
                ))

            conn.commit()
    conn.close()
    return
if __name__ == '__main__':
    import_locations(sys.argv[1])