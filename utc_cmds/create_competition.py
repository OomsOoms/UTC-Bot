import sqlite3
import pickle
from datetime import datetime

conn = sqlite3.connect('data/utc_database.db')

class Competition:

    def __init__(self, competition_name):

        self.competition_name = competition_name

        self.password = "UTC123" # Default placeholder

        self.competitors = {} # User ID:competitor object

        self.settings = {"host_users":[], "round_length":0, "live_results":False, "video_evidence":False, "start_date":0, "guilds":[]}

    def write(self):
        # Store the serialized data in the database

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
        cursor.execute("INSERT INTO competitions (competition_id, serialized_data) VALUES (?, ?)", (self.competition_id, serialized_data))
        conn.commit()
        cursor.close()



def find_competition(competition_id):
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the query to search for competition_id in the competitions table
    cursor.execute("SELECT * FROM competitions WHERE competition_id = ?", (competition_id,))

    # Fetch the results of the query
    result = cursor.fetchone()
    cursor.close()
    
    if result: result = pickle.loads(result[1])

    # Returns an object if found, returns None if not found
    return result


def reset_table(table_name):
    cursor = conn.cursor()
    
    try:
        # Delete all rows from the table
        cursor.execute(f"DELETE FROM {table_name}")
        
        # Commit the changes
        conn.commit()
        print(f"All rows from '{table_name}' have been deleted successfully.")
        
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        
    finally:
        # Close the cursor and the database connection
        cursor.close()

#reset_table("competitions")
#Competition("Test").write()