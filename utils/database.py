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


def execute_query(query_name, data=None, column_name=None):
    cursor = conn.cursor()

    queries = {
        "SELECT_solve_num": "SELECT solve_num FROM threads WHERE thread_id = ?",
        "SELECT_thread_data": "SELECT competition_id, event_id, round_type, value_1, value_2, value_3, value_4, value_5 FROM threads WHERE thread_id = ?",
        "SELECT_thread_info": "SELECT competition_id, event_id, user_id, round_type, solve_num FROM threads WHERE thread_id = ?",
        "SELECT_solve_count_trim": "SELECT formats.solve_count, formats.trim_fastest_n FROM threads JOIN events ON threads.event_id = events.event_id JOIN formats ON events.average_id = formats.average_id WHERE threads.competition_id = ? AND threads.user_id = ?",
        "SELECT_thread_values": "SELECT value_1, value_2, value_3, value_4, value_5 FROM threads WHERE thread_id = ?",
        "SELECT_scramble": "SELECT scramble FROM scrambles WHERE competition_id = ? AND event_id = ? AND scramble_num = ? AND round_type = ?",
        "SELECT_event_results": "SELECT * FROM results WHERE competition_id = ? AND event_id = ? ORDER BY average;",
        "SELECT_competition": "SELECT * FROM competitions WHERE competition_id = ?",

        "UPDATE_threads_value": f"UPDATE threads SET {column_name} = ? WHERE thread_id = ?",
        "UPDATE_thread_solve_num": "UPDATE threads SET solve_num = solve_num + 1 WHERE thread_id = ?",

        "INSERT_result": "INSERT INTO results (competition_id, event_id, user_id, guild_id, average_id, round_type_id, average, value_1, value_2, value_3, value_4, value_5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",

        "DELETE_thread_data": "DELETE FROM threads WHERE thread_id = ?",
    }

    query = queries.get(query_name)

    if not query:
        raise ValueError(f"Invalid query name: {query_name}")

    if column_name is not None:
        query = query.format(column_name=column_name)

    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)

    if query.upper().startswith('SELECT'):
        result = cursor
    else:
        result = None

    conn.commit()

    return result