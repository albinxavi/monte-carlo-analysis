import psycopg2

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

conn = None


def connect():
    try:
        global conn
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        print("Database connected successfully")
    except:
        print("Database not connected")


def execute_query(query):
    if not conn:
        connect()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def execute_query_and_get_data(query):
    if not conn:
        connect()
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()
