import sqlite3

# Create a connection to the database to import into other files
conn = sqlite3.connect('data/utc_database.db')

def export_sql_from_db(output_file):
    # Connect to the SQLite database
    cursor = conn.cursor()

    # Get the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cursor.fetchall()

    # Open the output file for writing SQL statements
    with open(output_file, 'w') as f:
        # Export schema for each table
        for table_name in table_names:
            table_name = table_name[0]
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            table_schema = cursor.fetchone()
            if table_schema:
                f.write(table_schema[0] + ";\n")

            # Export data for each table
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            if rows:
                column_names = [description[0] for description in cursor.description]
                for row in rows:
                    insert_statement = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES {row};\n"
                    f.write(insert_statement)

    # Close the database connection
    cursor.close()
