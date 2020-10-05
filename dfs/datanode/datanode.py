import os
import shutil

from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

base_path = '/dfs'


@app.route('/hello')
def hello():
    return Response(status=200, response="Hello from datanode!")


@app.route('/init')
def init():
    os.system('rm -rf ' + base_path + "/*")
    total, used, free = shutil.disk_usage('/')
    return Response(status=200, response=str(free).encode())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
