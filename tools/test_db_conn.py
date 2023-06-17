import os
import psycopg2

def main():
    DATABASE_URL = os.environ['DATABASE_URL']
    print(f"connecting to {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        print(db_version)
    except Exception as error:
        print(f"Error: {error}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
