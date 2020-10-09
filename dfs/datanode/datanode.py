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


@app.route('/ls')
def ls():
    # Get params
    dirname = request.args.get('dirname')
    files = os.listdir(dirname)

    response = ''
    for file in files:
        response += file + '\t'

    return Response(status=200, response=response)


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
    return Response(status=200, response=f'Copy of file {source} was created at {destination}')


@app.route('/rm')
def rm():
    filename = request.args.get('filename')
    os.system('rm ' + base_path + '/' + filename)
    return Response(status=200, response=f'File {filename} was deleted.')


@app.route('/rmdir')
def rmdir():
    dirname = request.args.get('dirname')
    os.system('rm -rf ' + base_path + '/' + dirname)
    return Response(status=200, response=f'Directory {dirname} was deleted.')


@app.route('/move')
def move():
    filename = request.args.get('filename')
    destination_dir = request.args.get('destination_dir')
    os.system('mv ' + base_path + '/' + filename + " " + base_path + '/' + destination_dir)

    return Response(status=200, response=f'File {filename} was moved to directory {destination_dir}.')


@app.route('/info')
def info():
    # Get params
    filename = request.args.get('filename')

    try:
        output = subprocess.check_output('stat ' + filename, shell=True)
        response = "The information:\n" + output
    except BaseException as e:
        response = e

    # response = "The information:\n" + output
    return Response(status=200, response=response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
