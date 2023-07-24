import sqlite3

# Create a connection to the database
conn = sqlite3.connect('data/utc_database.db')
cursor = conn.cursor()

# Delete all tables to add new replacements
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

# Create competitions table
cursor.execute('''
    CREATE TABLE competitions (
        competition_id TEXT PRIMARY KEY,
        competition_name TEXT,
        organisers_id TEXT,
        embed_info TEXT
    )
''')

# Create competition_events table
cursor.execute('''
    CREATE TABLE competition_events (
        competition_id TEXT,
        event_id TEXT,
        FOREIGN KEY (event_id) REFERENCES events(event_id)
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id)
    )
''')

# Create scrambles table
cursor.execute('''
    CREATE TABLE scrambles (
        scramble_id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        event_id TEXT,
        round_type TEXT,
        scramble_num INTEGER,
        scramble TEXT,
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id)
    )
''')

# Create events table
cursor.execute('''
    CREATE TABLE events (
        event_id TEXT PRIMARY KEY,
        event_name TEXT,
        format TEXT,
        average_id TEXT,
        FOREIGN KEY (average_id) REFERENCES formats(average_id)
    )
''')

# Create formats table
cursor.execute('''
    CREATE TABLE formats (
        average_id TEXT PRIMARY KEY,
        average_name TEXT,
        sort_by TEXT,
        sort_by_second TEXT,
        solve_count INTEGER,
        trim_fastest_n INTEGER,
        trim_slowest_n INTEGER
    )
''')

# Create results table
cursor.execute('''
    CREATE TABLE results (
        result_id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        event_id TEXT,
        user_id INTEGER,
        guild_id INTEGER,
        average_id TEXT,
        round_type_id TEXT,
        pos INTEGER,
        average INTEGER,
        value_1 INTERGER,
        value_2 INTEGER,
        value_3 INTEGER,
        value_4 INTEGER,
        value_5 INTEGER,
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id),
        FOREIGN KEY (average_id) REFERENCES formats(average_id)
    )
''')

# Create threads table
cursor.execute('''
    CREATE TABLE threads (
        thread_id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        event_id TEXT,
        user_id INTEGER,
        round_type TEXT,
        solve_num INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(event_id),
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id)
    )
''')

cursor.execute("INSERT INTO competitions (competition_id, competition_name, organisers_id, embed_info) VALUES (?, ?, ?, ?)", (123, 123, 760616986568163348, "competition info from db"))
cursor.execute("INSERT INTO competitions (competition_id, competition_name, organisers_id, embed_info) VALUES (?, ?, ?, ?)", (456, 456, 760616986568163348, "competition info from db 2"))
cursor.execute("INSERT INTO events (event_id, event_name, format, average_id) VALUES (?, ?, ?, ?)", ("333", "3x3 Cube", "time", "a"))
cursor.execute("INSERT INTO events (event_id, event_name, format, average_id) VALUES (?, ?, ?, ?)", ("222", "2x2 Cube", "time", "a"))
cursor.execute("INSERT INTO competition_events (competition_id, event_id) VALUES (?, ?)", (123, "333"))
cursor.execute("INSERT INTO competition_events (competition_id, event_id) VALUES (?, ?)", (123, "222"))
cursor.execute("INSERT INTO formats (average_id, average_name, sort_by, sort_by_second, solve_count, trim_fastest_n, trim_slowest_n) VALUES (?, ?, ?, ?, ?, ?, ?)", ("a", "Average of 5", "average", "single", 5, 1, 1))
cursor.execute("INSERT INTO results (result_id, competition_id, event_id, user_id, guild_id, average_id, round_type_id, pos, average, value_1, value_2, value_3, value_4, value_5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (1, "123", 333, 760616986568163348, 988085977719402536, "a", "1", 1, 1234, 1234, 1234, 1234, 1234, 1234))

# Commit the changes and close the connection
conn.commit()
conn.close()
