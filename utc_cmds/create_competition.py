import sqlite3
import pickle
from datetime import datetime


class Competition:

    def __init__(self, competition_name):

        self.competition_name = competition_name

        self.competitors = [] # List of competitor objects specific to each competition

        self.settings = {"host_users":[], "round_length":0, "live_results":False, "video_evidence":False, "start_date":0, "guilds":[]}

    def write(self):
        # Store the serialized data in the database
        with sqlite3.connect('data/utc_database.db') as conn:
            cursor = conn.cursor()

            # Get unique ID
            cursor.execute("SELECT COUNT(*) FROM competitions")
            row_count = cursor.fetchone()[0]
            number = str(row_count).zfill(3)

            # Standardise names into PascalCase
            words = [word.capitalize() for word in self.competition_name.lower().split()]
            id = ''.join(words)

            # Get the date in format mmyy
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month

            # Create competition ID
            self.competition_id = f"{id}{month:02d}{str(year)[-2:]}{number}"

            # Insert the serialized object into the database
            serialized_data = pickle.dumps(self)
            print(serialized_data)
            cursor.execute("INSERT INTO competitions (competition_id, serialized_data) VALUES (?, ?)", (self.competition_id, serialized_data))
            conn.commit()