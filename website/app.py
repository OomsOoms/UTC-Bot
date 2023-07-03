from flask import Flask, render_template
from views import discord

app = Flask(__name__)
app.register_blueprint(discord)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
