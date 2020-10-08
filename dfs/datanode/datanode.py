import os
import shutil
import subprocess
from flask import Flask, Response, request
from flask_cors import CORS
import os.path
import time

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


@app.route('/mkdir')
def mkdir():
    # Get params
    dirname = request.args.get('dirname')
    os.system('mkdir ' + base_path + '/' + dirname)
    return Response(status=200, response=f'Directory {dirname} was created.')


@app.route('/copy')
def copy():
    # Get params
    source = request.args.get('source')
    destination = request.args.get('destination')
    os.system('cp ' + base_path + '/' + source + ' ' + base_path + '/' + destination)
    return Response(status=200, response=f'Copy of file {source} was created with name {destination}')


@app.route('/info')
def info():
    # Get params
    filename = request.args.get('filename')
    # file = base_path + '/' + filename
    # result = 'File         :' + filename + '\n'
    # result += 'Access time  :' + time.ctime(os.path.getatime(file)) + '\n'
    # result += 'Modified time:' + time.ctime(os.path.getmtime(file)) + '\n'
    # result += 'Change time  :' + time.ctime(os.path.getctime(file)) + '\n'
    # result += 'Size         :' + os.path.getsize(file)
    # response = f'The information:\n' + result
    return Response(status=200, response="Hello my friend")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
