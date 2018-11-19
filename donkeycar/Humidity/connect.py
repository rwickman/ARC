import psycopg2
from config import config

def connect():
    # Connect to the PostGreSQL database server
    conn = None
    try:
        # Read connection parameters
        params = config()
        
        # Connect to the PostGreSQL server
        print("Connection to the PostGreSQL server")
        conn = psycopg2.connect(**params)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a statement
        print("PostGreSQL database version:")
        cur.execute('SELECT version()')
        
        # Display the PostGreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        
        # Close the communication with the PostGreSQL
        cur.close()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')
if __name__ == "__main__":
    connect()