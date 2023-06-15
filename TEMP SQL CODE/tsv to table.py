import sqlite3
import csv

# Connect to the database
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Optional Step 3: Drop the existing table
cursor.execute("DROP TABLE events")

# Read the TSV file and retrieve the header (column names)
tsv_file = 'temp.tsv'
with open(tsv_file, 'r') as file:
    tsv_data = csv.reader(file, delimiter='\t')
    header = next(tsv_data)  # Get the header row

# Generate the CREATE TABLE statement based on the columns in the TSV file
table_name = 'events'
column_definitions = ', '.join(f"{column} TEXT" for column in header)  # Assume all columns as TEXT
create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"

# Create the table
cursor.execute(create_table_query)

# Insert the data into the table
with open(tsv_file, 'r') as file:
    tsv_data = csv.reader(file, delimiter='\t')
    next(tsv_data)  # Skip header row if exists
    for row in tsv_data:
        cursor.execute(f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(row))})", row)

# Commit the changes
connection.commit()

# Close the connection
connection.close()
