from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# datanodes = ["3.16.213.82:7777", "18.216.176.176:7777", "3.134.115.22:7777"]
datanodes = ["10.0.15.11:7777","10.0.15.12:7777","10.0.15.13:7777"]

@app.route('/hello')
def hello():
    print("Hello from namenode")
    for datanode in datanodes:
        requests.get("http://" + datanode + "/hello")
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)  # , debug=True, use_reloader=False)
