import sqlite3

conn = sqlite3.connect(r'C:\Users\test\.n8n\database.sqlite')
cur = conn.cursor()

table_type = 'table'
cur.execute("SELECT name FROM sqlite_master WHERE type=?", (table_type,))
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

for t in tables:
    if 'api' in t.lower() or 'key' in t.lower() or 'user' in t.lower():
        print(f"\n--- {t} ---")
        try:
            cur.execute(f"SELECT * FROM {t} LIMIT 5")
            cols = [d[0] for d in cur.description]
            print("Columns:", cols)
            for row in cur.fetchall():
                print(row)
        except Exception as e:
            print(f"Error: {e}")

conn.close()
