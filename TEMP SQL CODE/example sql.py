import sqlite3

# Establish a connection to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Execute SQL queries
cursor.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
cursor.execute("INSERT INTO employees (name, age) VALUES (?, ?)", ("John Doe", 25))

# Fetch data from the database
cursor.execute("SELECT * FROM employees")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Update data in the database
cursor.execute("UPDATE employees SET age = ? WHERE id = ?", (30, 1))

# Delete data from the database
cursor.execute("DELETE FROM employees WHERE id = ?", (1,))

# Fetch table names from the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

# Print the table names
for table in tables:
    print(table[0])

# Delete a table from the database
cursor.execute("DROP TABLE IF EXISTS employees")

# Fetch table names from the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

# Print the table names
for table in tables:
    print(table[0])

# Commit the changes
conn.commit()

# Close the connection
conn.close()

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

# Create the first table
cursor.execute('''CREATE TABLE Table1 (
                    id INTEGER PRIMARY KEY,
                    other_column TEXT
                )''')

# Create the second table with a foreign key reference
cursor.execute('''CREATE TABLE Table2 (
                    id INTEGER PRIMARY KEY,
                    table1_id INTEGER,
                    other_column TEXT,
                    FOREIGN KEY (table1_id) REFERENCES Table1(id)
                )''')

# Commit the changes and close the connection
conn.commit()
conn.close()



