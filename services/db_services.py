import psycopg2

DB_NAME = "ktjdnamf"
DB_USER = "ktjdnamf"
DB_PASS = "HeKEtWagEWZER419HvLekPwvIru6fO3e"
DB_HOST = "drona.db.elephantsql.com"
DB_PORT = "5432"

try:
    conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    print("Database connected successfully")
except:
    print("Database not connected")


def execute_query(query):
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def execute_query_and_get_data(query):
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()
