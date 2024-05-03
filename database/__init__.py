import sqlite3
import shutil
from datetime import datetime

from utils.custom_logger import CustomLogger

class DatabaseManager:

    def __init__(self, *, database_path) -> None:
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()

        formatted_datetime = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        backup_path = f"database/backup/{formatted_datetime}.db"
        shutil.copy(database_path, backup_path)

        with open("database/schema.sql") as file:
            self.cursor.executescript(file.read())
        self.conn.commit()


    def select_competition(self, competition_id):
        self.cursor.execute("SELECT * FROM competitions WHERE competition_id = ?", (competition_id,))
        return self.cursor.fetchone()
    

    def check_participation(self, competition_id, user_id, event_id, round_type):
        self.cursor.execute("SELECT table_name, value FROM (SELECT 'threads' AS table_name, thread_id AS value, competition_id, user_id, event_id, round_type FROM threads UNION ALL SELECT 'results' AS table_name, result_id AS value, competition_id, user_id, event_id, round_type FROM results) combined WHERE competition_id = ? AND user_id = ? AND event_id = ? AND round_type = ?", (competition_id, user_id, event_id, round_type))
        return self.cursor.fetchone()
    

    def insert_thread(self, thread_id, user_id, event_id, competition_id, round_type):
        self.cursor.execute("INSERT INTO threads (thread_id, user_id, event_id, competition_id, solve_num, round_type) VALUES (?, ?, ?, ?, 1, ?)", (thread_id, user_id, event_id, competition_id, round_type))
        self.conn.commit()


    def select_events(self):
        self.cursor.execute("SELECT * FROM events")
        return self.cursor.fetchall()


    def insert_competition(self, competition_name, competition_id, host_id, event_1, event_2, event_3, event_4, event_5):
        self.cursor.execute(f"INSERT INTO competitions (competition_id, competition_name, host_id, active) VALUES (?, ?, ?, 1)", (competition_id, competition_name, host_id))

        events = [event_1, event_2, event_3, event_4, event_5]
        for event in events:
            if event:
                self.cursor.execute("INSERT INTO competition_events (competition_id, event_id) VALUES (?, ?)", (competition_id, event))
        # TODO: Add scramble generation
        self.conn.commit()

    def select_competition_events(self, competition_id):
        self.cursor.execute("SELECT c.competition_id, c.event_id, e.event_name, c.video_evidence FROM competition_events c JOIN events e ON c.event_id = e.event_id WHERE c.competition_id = ?", (competition_id,))
        return self.cursor.fetchall()
    

database_manager = DatabaseManager(database_path="database/utc_database.db")

