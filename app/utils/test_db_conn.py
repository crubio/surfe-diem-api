import os
import psycopg2
import dotenv

dotenv.load_dotenv()

def test():
    DATABASE_URL = os.environ['DATABASE_URL']
    print(f"connecting to {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        print(db_version)
    except Exception as error:
        print(f"Error: {error}")
    finally:
        conn.close()
