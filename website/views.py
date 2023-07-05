from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import os
import requests

discord = Blueprint("discord", __name__)

load_dotenv() # Envoriment variables
BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")

@discord.route("/send_message", methods=["POST"])
def send_message():

    response = requests.post(
        f"https://discord.com/api/v9/channels/1125592899908817038/messages",
        headers={"Authorization": f"Bot {BOT_TOKEN}"},
        json={"content": "Hello from the website!"}
    )

    if response.status_code == 200:
        return jsonify({"status": "success", "message": "Message sent successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to send message"})
