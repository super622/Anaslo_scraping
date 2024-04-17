from multiprocessing import Process
from flask import Flask
from flask_cors import CORS

from main import AnaSloData

app = Flask(__name__)
CORS(app)
processes = []

def get_data_from_site(type):
    anaslo = AnaSloData()
    if type == 'all_data':
        result = anaslo.get_all_datas(True)
    else:
        result = anaslo.get_all_datas(False)

@app.route("/", methods=["GET"])
def get_root():
    return "Server is running"

@app.route("/get_all_data", methods=["POST"])
def get_all_data():
    p = Process(target=get_data_from_site, args=("all_data",)).start()
    processes.append(p)
    return "Running"

@app.route("/get_latest_data", methods=["POST"])
def get_latest_data():
    p = Process(target=get_data_from_site, args=("latest_data",)).start()
    processes.append(p)
    return "Running"

def run(host, port):
    app.run(host=host, port=port)

# if __name__ == '__main__':
#     for _ in range(5):  # Run 5 processes
#         p = Process(target=app.run)
#         p.start()