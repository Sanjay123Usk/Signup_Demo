import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT * FROM users")
rows = c.fetchall()

print("Registered Users:")
for row in rows:
    print(row)

conn.close()
