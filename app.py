from multiprocessing import Process
from flask import Flask, request
from flask_cors import CORS
import json

from main import AnaSloData

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def get_root():
    return "Server is running"

@app.route("/get_all_data", methods=["POST"])
def get_all_data():
    anaslo = AnaSloData()
    result = anaslo.all_data()
    return "Running"

@app.route("/get_latest_data", methods=["POST"])
def get_latest_data():
    anaslo = AnaSloData()
    result = anaslo.latest_data()
    return "Running"


def run(host, port):
    app.run(host=host, port=port)

if __name__ == '__main__':
    for _ in range(5):  # Run 5 processes
        p = Process(target=app.run)
        p.start()