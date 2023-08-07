import sqlite3


class DatabaseHandler:
    def __init__(self):
        self.db_path ="../data/utc_database.db"
        self.conn = None
        self.cursor = None

    def execute_query(self, query_name, data=None, table_name=None):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

        conn = sqlite3.connect("../data/utc_database.db")
        self.cursor = conn.cursor()

        queries = {
            "SELECT_table": f"SELECT * FROM {table_name}",
            "SELECT_results": "SELECT * FROM results WHERE user_id = ?",
            "INSERT_competition": "INSERT INTO competitions (competition_name, competition_id, extra_info) VALUES (?, ?, ?)",
            "INSERT_competition_events": "INSERT INTO competition_events (competition_id, competition_id) VALUES (?, ?)",
            "INSERT_scramble": "INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES (?, ?, ?, ?, ?)",
            "SELECT_event_solve_count": "SELECT e.event_name, e.event_id, f.solve_count FROM events AS e JOIN formats AS f ON e.average_id = f.average_id",
        }

        query = queries.get(query_name)

        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        if query.upper().startswith('SELECT'):
            return self.cursor
        else:
            return

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()

