from flask import Flask, request
from flask_cors import CORS
import json

from main import AnaSloData

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def get_root():
    return "Server is running"

@app.route("/get_all_data", methods=["GET"])
def getdata():
    anaslo = AnaSloData()
    result = anaslo.main()
    return json.dumps(result)

def run(host, port):
    app.run(host=host, port=port)

if __name__ == '__main__':
    for _ in range(5):  # Run 5 processes
        p = Process(target=app.run)
        p.start()