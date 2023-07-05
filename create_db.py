import sqlite3

# Create a connection to the database
conn = sqlite3.connect('data/utc_database.db')
cursor = conn.cursor()

# Create competitions table
cursor.execute('''
    CREATE TABLE competitions (
        competition_id INTEGER PRIMARY KEY,
        competition_name TEXT
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

cursor.execute("INSERT INTO competitions (competition_id, competition_name) VALUES (?, ?)", (123, 123))
cursor.execute("INSERT INTO events (event_id, event_name, format, average_id) VALUES (?, ?, ?, ?)", ("333", "3x3 Cube", "time", "a"))
cursor.execute("INSERT INTO events (event_id, event_name, format, average_id) VALUES (?, ?, ?, ?)", ("222", "2x2 Cube", "time", "a"))
cursor.execute("INSERT INTO formats (average_id, average_name, sort_by, sort_by_second, solve_count, trim_fastest_n, trim_slowest_n) VALUES (?, ?, ?, ?, ?, ?, ?)", ("a", "Average of 5", "average", "single", 5, 1, 1))

# Commit the changes and close the connection
conn.commit()
conn.close()
