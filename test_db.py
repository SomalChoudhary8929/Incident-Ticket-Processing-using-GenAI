from db import get_connection

def test_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    cur.close()
    conn.close()
    print("✅ DB Connected. Current time:", result[0])

if __name__ == "__main__":
    test_db()
