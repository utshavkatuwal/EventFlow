import sqlite3
conn = sqlite3.connect('C:/Projects/EventFlow/backend/eventflow.db')
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = c.fetchall()
print("Tables:", tables)
for t in tables:
    if 'categ' in t[0].lower():
        print(f"\n--- {t[0]} ---")
        c.execute(f'SELECT * FROM {t[0]}')
        for r in c.fetchall():
            print(r)
conn.close()