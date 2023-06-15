import sqlite3

# Connect to the database
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

cursor.execute("DROP TABLE temp")
connection.commit()

# Step 1: Create a new table with the desired schema
cursor.execute("CREATE TABLE temp (average_id TEXT PRIMARY KEY, average_name TEXT, sort_by TEXT, sort_by_second TEXT, solve_count INTEGER, trim_fastest_n INTEGER, trim_slowest_n INTEGER)")
connection.commit()

# Step 2: Copy data from the existing table to the new table
cursor.execute("INSERT INTO temp SELECT * FROM formats")
connection.commit()

# Optional Step 3: Drop the existing table
cursor.execute("DROP TABLE formats")
connection.commit()

# Step 4: Rename the new table to the original table name
cursor.execute("ALTER TABLE temp RENAME TO formats")

connection.commit()


# Close the connection
connection.close()
