import psycopg2
import json
from app.config import settings

conn = psycopg2.connect(
   database=settings.database_name, user=settings.database_username, password=settings.database_password,
   host=settings.database_hostname, port=settings.database_port
)

# test runner against fake table
def my_func(file = None):
    '''runs the import from our json file'''
    # assume we have a json from a file scrape
    with open('stations_list.json') as data_file:
        data = json.load(data_file)
        for v in data:
            print(v["location_id"])

    # cursor = conn.cursor()

    # cursor.execute('''INSERT INTO locations_test(name) VALUES('station 1')''')

    # conn.commit()
    # print("Inserted records...")

    # conn.close()
if __name__ == '__main__':
    my_func()