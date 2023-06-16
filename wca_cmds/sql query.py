import sqlite3
import time

conn = sqlite3.connect('data/wca_database.db')

# Create a cursor
cursor = conn.cursor()

start = time.perf_counter()

#cursor.execute("""
#    SELECT persons.*, rankssingle.eventId, rankssingle.countryRank
#    FROM persons
#    INNER JOIN rankssingle ON persons.id = rankssingle.personId
#    WHERE rankssingle.eventId = ?
#    AND persons.countryId = ?
#    """, ("333", "United Kingdom"))

#results = cursor.fetchmany(1000)

cursor.execute("SELECT id FROM persons WHERE id = ?", ("2018NETT01",))

results = cursor.fetchone()

print(time.perf_counter()-start)

print(len(results))
print(type(results))


# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()