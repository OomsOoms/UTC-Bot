from flask import render_template, redirect, url_for, session, request, Response, jsonify
import os
import secrets
import requests

from dotenv import load_dotenv

load_dotenv()

from app import app

app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(24))
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")

@app.route("/")
def index():
    return session.get("access_token", {})
    
@app.route("/login")
def login():
    # Redirect the user to Discord's OAuth2 authorization endpoint
    return redirect(f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&scope=identify&response_type=code&redirect_uri={DISCORD_REDIRECT_URI}")

@app.route("/callback")
def callback():
    # After the user grants permission on Discord, they'll be redirected back to this route
    # with a "code" query parameter in the URL
    code = request.args.get("code")
    print(code)

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