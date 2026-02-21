import sqlite3

c = sqlite3.connect('data/analytics.db')

# Show all tables and row counts
for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    count = c.execute(f"SELECT COUNT(*) FROM [{t[0]}]").fetchone()[0]
    print(count, "rows in", t[0])

c.close()