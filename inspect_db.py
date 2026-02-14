import sqlite3
import os

db_path = 'backend/database.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Tables ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(table[0])

if ('providers',) in tables:
    print("\n--- Providers Data ---")
    cursor.execute("SELECT id, service_type, location, address, background_verified FROM providers")
    for row in cursor.fetchall():
        print(row)
else:
    print("\n'providers' table not found.")

conn.close()
