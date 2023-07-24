import sqlite3
import requests
import zipfile
import json
import os
import glob
import csv
from dateutil import parser


def create_database():
    # Establish a connection to the database
    try:
        os.remove('data/wca_database.db')
    except:
        pass
    conn = sqlite3.connect('data/wca_database.db')

    # Create a cursor
    cursor = conn.cursor()

    # Get a list of TSV files in the folder
    tsv_files = glob.glob('data/WCA_export.tsv/*.tsv')

    # Iterate over the TSV files
    for tsv_file in tsv_files:
        file_name = os.path.basename(tsv_file)
        table_name = file_name.split('.')[0]
        table_name = table_name.replace("WCA_export_", "").lower()

        if table_name in ["persons", "results", "rankssingle", "ranksaverage"]:

            # Create the table with columns from the TSV file
            with open(tsv_file, 'r', encoding='utf-8') as file:
                # Read the TSV data using the CSV module
                tsv_data = csv.reader(file, delimiter='\t')

                # Get the column names from the first row of TSV data
                columns = next(tsv_data)

                # Generate the CREATE TABLE statement
                create_table_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"

                # Execute the CREATE TABLE statement
                cursor.execute(create_table_query)

                # Insert the data into the table
                insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(columns))})"
                cursor.executemany(insert_query, tsv_data)

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()


def check_and_download_export():
    api_url = 'https://www.worldcubeassociation.org/api/v0/export/public'

    # Send GET request to the API endpoint
    response = requests.get(api_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()

        # Extract export information
        export_date = data['export_date']
        sql_url = data['tsv_url']

        try:
            with open("data/WCA_export.tsv/metadata.json", "r") as f:
                current_export_date = json.loads(f.read())["export_date"]
                current_export_date = parser.parse(current_export_date)
        except FileNotFoundError:
            current_export_date = "None"
            
        # Convert date strings to datetime objects, ignoring the time zone
        export_date = parser.parse(export_date)

        print(export_date)
        print(current_export_date)

        
        # Compare the dates
        if export_date != current_export_date:

            print("Downloading export")
            response = requests.get(sql_url, stream=True)
            with open("data/WCA_export.tsv.zip", 'wb') as file:
                file.write(response.content)

            print("Extracting export")
            # Extract the file
            with zipfile.ZipFile("data/WCA_export.tsv.zip", 'r') as zip_ref:
                zip_ref.extractall("data/WCA_export.tsv")
            os.remove("data/WCA_export.tsv.zip")

            print("Done")

            print("creating databsae")
            create_database()

check_and_download_export()