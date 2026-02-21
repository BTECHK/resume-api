import sqlite3
conn = sqlite3.connect('data/analytics.db')
conn.execute("DROP TABLE IF EXISTS recruiter_queries_500k")
conn.execute("DROP TABLE IF EXISTS recruiter_queries_5m")
conn.execute("VACUUM")
conn.close()
print("Dropped 500k and 5m tables, vacuumed database")
