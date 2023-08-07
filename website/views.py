from flask import render_template, redirect, url_for, session, request, Response, jsonify
import os
import secrets
import sqlite3
import requests

from app import app
from database import DatabaseHandler

app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(24))

# Replace the following placeholders with your Discord app credentials
DISCORD_CLIENT_ID = "1028068938476695593"
DISCORD_CLIENT_SECRET = "19GOn7pRoP8VgqDssxFfNJ3dXm7uaZDd"
DISCORD_REDIRECT_URI = "http://192.168.0.231:5000/callback"  # Replace with your callback URL

# Configuration
DATABASE = '../data/utc_database.db'


@app.route("/")
def index():
    session["redirect_url"] = request.args.get("redirect_to", "/")
    print(session)
    return render_template('index.html')

# tables page
@app.route('/tables')
def tables():
    # Get a list of all tables in the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('tables.html', tables=tables)

@app.route('/create_competition', methods=['GET', 'POST'])
def create_competition():
    #if "access_token" in session:
        if request.method == 'POST':
            competition_name = request.form['competitionName']
            competition_id = request.form['competitionId']
            event_ids = request.form.getlist('eventName[]')
            average_ids = request.form.getlist('averageId[]')
            scrambles = request.form.getlist('scramble[]')
            extra_info = request.form['extraInfo']

            db_handler = DatabaseHandler()

            db_handler.execute_query("INSERT_competition", (competition_name, competition_id, extra_info))#, session.get("user_data").get("id")))
            db_handler.execute_query("INSERT_competition_events", (competition_id, event_id))


            for scramble_num, (event_id, average_id, scramble) in enumerate(zip(event_ids, average_ids, scrambles), start=1):
                db_handler.execute_query("INSERT_scramble", (event_id, average_id, "f", scramble_num, scramble))

            db_handler.close()

            return "Competition added to database"
        
        db_handler = DatabaseHandler()

        cursor = db_handler.execute_query("SELECT_event_solve_count")

        event_data = cursor.fetchall()

        return render_template("create_competition.html", event_data=event_data)
    #else:
        return redirect(url_for("login"))

# Add the route for the table view page
@app.route('/table/<table_name>')
def table(table_name):

    db_handler = DatabaseHandler()

    cursor = db_handler.execute_query("SELECT_table", table_name=table_name)
    data = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    db_handler.close()

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

@app.route('/execute_query', methods=['POST'])
def execute_query():

    query = request.form['query']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)

    conn.commit()
    conn.close()

    # Convert the data to a list of dictionaries
    
    return render_template("data.html", data)



# Another route that uses the stored user data
@app.route("/profile")
def profile():
    if "access_token" in session:
        db_handler = DatabaseHandler()

        event_data = db_handler.execute_query("SELECT_results", (session.get("user_data").get("id"),)).fetchall()

        db_handler.close()

        return render_template('profile.html', user_data=session.get("user_data"), event_data=event_data)
    else:
        return redirect(url_for("login"))
    
@app.route("/login")
def login():
    # Redirect the user to Discord's OAuth2 authorization endpoint
    return redirect(f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&scope=identify&response_type=code&redirect_uri={DISCORD_REDIRECT_URI}")

@app.route("/callback")
def callback():
    # After the user grants permission on Discord, they'll be redirected back to this route
    # with a "code" query parameter in the URL
    code = request.args.get("code")

    # Now we'll exchange the code for an access token
    # In a real application, you should do this using a secure method (e.g., POST request)
    # but for simplicity, we'll do a GET request here
    # Note: This is not the recommended way to handle tokens in production.
    # Use a secure method to obtain and store tokens.
    # Read more: https://discord.com/developers/docs/topics/oauth2#token-authorization-code-grant
    
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": "identify",
    }

    response = requests.post("https://discord.com/api/oauth2/token", data=data)

    access_token = response.json().get("access_token")

    # Store the access token in the user's session
    session["access_token"] = access_token

    # Get user information using the access token
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

    session["user_data"] = response.json()

    return redirect("/")


