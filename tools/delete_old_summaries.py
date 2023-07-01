import psycopg2
import os
import logging
from dotenv import load_dotenv

load_dotenv()

from station_ids import *

conn = psycopg2.connect(
   database=os.environ.get('DATABASE_NAME'), user=os.environ.get('DATABASE_USERNAME'), password=os.environ.get('DATABASE_PASSWORD'),
   host=os.environ.get('DATABASE_HOSTNAME'), port=os.environ.get('DATABASE_PORT')
)

def delete_old_summaries():
    '''deletes summaries older than 48 hours'''
    cursor = conn.cursor()
    try:
        cursor.execute('''DELETE FROM locations_noaa_summary WHERE date_created < NOW() - INTERVAL '48 hours';''')
        conn.commit()
        logging.info(f"Deleted {cursor.rowcount} rows")
        print(f"Deleted {cursor.rowcount} rows")
    except Exception as error:
        logging.warning(f"Error deleting rows: {error}")
        conn.rollback()
    conn.close()
    return

if __name__ == '__main__':
    delete_old_summaries()