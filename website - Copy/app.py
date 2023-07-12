from flask import Flask

app = Flask(__name__)

# Import the views module
from views import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
