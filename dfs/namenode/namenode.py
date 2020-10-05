from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)


datanodes = ["10.0.15.11:7777","10.0.15.12:7777","10.0.15.13:7777"]

@app.route('/hello')
def hello():
    res = ""
    for datanode in datanodes:
        res += requests.get("http://" + datanode + "/hello") + "\n--\n"

    return Response(status=200, response="Hello from namenode\n"+res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)  # , debug=True, use_reloader=False)
