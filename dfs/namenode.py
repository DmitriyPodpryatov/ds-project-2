import json
from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json
app = Flask(__name__)
CORS(app)

datanodes = ["0.0.0.0:7777", '3.129.14.225:7777']


@app.route('/hello')
def hello():
    print("Hello from namenode")
    for datanode in datanodes:
        requests.get("http://" + datanode + "/hello")
    return Response(status=200)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)#, debug=True, use_reloader=False)
