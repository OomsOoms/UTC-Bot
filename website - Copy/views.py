from flask import render_template, request, jsonify, Response
import sqlite3
import json

from app import app

# Configuration
DATABASE = '../data/utc_database.db'

# Home page
@app.route('/')
def index():
    # Get a list of all tables in the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', tables=tables)

@app.route('/table_data', methods=['POST'])
def table_data():
    table_name = request.form['table_name']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get all data from the selected table
    cursor.execute(f'SELECT * FROM {table_name}')
    data = cursor.fetchall()

    conn.close()

    return jsonify(data)

@app.route('/execute_query', methods=['POST'])
def execute_query():
    query = request.form['query']
    print(query)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    data = cursor.fetchall()

    conn.commit()
    conn.close()

    return json.dumps(data)

# Add the route for the table view page
@app.route('/table/<table_name>')
def table(table_name):
    # Fetch data from the selected table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    data = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    cursor.close()
    conn.close()

    return render_template('table.html', table_name=table_name, data=data, columns=columns)

# Route to handle the delete button
@app.route('/delete/<table>/<int:record_id>', methods=['POST'])
def delete_record(table, record_id):
    column_name = request.form.get('column_name')
    print(record_id, table, column_name)
    
    # Handle the deletion logic for the record with the given record_id in the specified table
    # ...
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(f"DELETE FROM {table} WHERE {column_name} = ?", (record_id,))
    data = cursor.fetchall()

    conn.commit()
    conn.close()
    return Response(status=204)

# Route to handle the edit button
@app.route('/edit/<table>/<int:record_id>', methods=['POST'])
def edit_record(table, record_id):
    column_name = request.form.get('column_name')
    print(record_id, table, column_name)
    
    return Response(status=204)
