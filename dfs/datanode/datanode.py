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
    return Response(status=200, response=str(free))


@app.route('/touch')
def touch():
    # Get params
    filename = request.args.get('filename')
    os.system('touch ' + base_path + '/' + filename)
    return Response(status=200, response=f'File {filename} was created.')


@app.route('/copy')
def copy():
    # Get params
    source = request.args.get('source')
    destination = request.args.get('destination')
    os.system('cp ' + base_path + '/' + source + ' ' + destination)
    return Response(status=200, response=f'Copy of file {source} was created with name {destination}.')


@app.route('/info')
def info():
    # Get params
    filename = request.args.get('filename')

    # not sure that os.system returns output, but will see
    result = os.system('stat ' + base_path + '/' + filename)
    response = f'The information about file {filename}:\n' + result
    return Response(status=200, response=response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
