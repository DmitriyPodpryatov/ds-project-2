from flask import Flask, Response, request
from flask_cors import CORS
import os
import requests


def valid_path(path: str):
    if path[0] != '/':
        # No root '/' => add '/' at the beginning
        path = '/' + path

    return path


class FileSystem:
    def __init__(self):
        self.root = FileSystem.File('/', is_dir=True, children={})

    class File:
        def __init__(self, name: str, is_dir: bool, parent=None, children=None, location: [] = None):
            if children is None:
                children = {}

            self.name = name
            self.children = children
            self.parent = parent
            self.is_dir = is_dir
            self.location = location

    def find_node(self, path: str):
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None:
            return current_node.location
        return []

    def add_node(self, path: str, is_dir: bool, location: list):
        path = valid_path(path)

        directories = path.split('/')[1:]
        current_node = self.root

        for dir in directories[:-1]:
            current_node = current_node.children.get(dir)

        new_node = FileSystem.File(directories[-1], is_dir, parent=current_node, children={}, location=location)
        current_node.children.update({directories[-1]: new_node})

    def update_location(self, path: str, location: str):
        path = valid_path(path)

        directories = path.split('/')[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        current_node.location.append(location)

    def dir_exists(self, path: str):
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None and current_node.is_dir:
            return True
        else:
            return False

    def file_exists(self, path: str):
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            try:
                current_node = current_node.children.get(dir)
            except AttributeError:
                # No children => wrong path
                return None

        if current_node is not None and not current_node.is_dir:
            return True
        else:
            return False


app = Flask(__name__)
CORS(app)
datanodes = ["10.0.15.11:7777", "10.0.15.12:7777", "10.0.15.13:7777"]

fs: FileSystem


@app.route('/hello')
def hello():
    res = "Hello from namenode!\n\n"
    for datanode in datanodes:
        res += requests.get("http://" + datanode + "/hello").text + "\n"
    return Response(status=200, response=res)


@app.route('/init')
def init():
    global fs
    fs = FileSystem()

    result = 0
    for datanode in datanodes:
        try:
            response = requests.get("http://" + datanode + "/init")
        except requests.exceptions.RequestException:
            continue
        result += int(response.content)

    storage = "The available storage is " + str(round(result // len(datanodes) / (1024 * 1024), 2)) + " MB"
    return Response(status=200, response=storage)


@app.route('/touch')
def touch():
    # Get params
    filename = request.args.get('filename')

    # Create file if it does not exists
    global fs
    response = 'Failed'

    # True (exists), False (doesn't exist), or None (error)
    exists = fs.file_exists(filename)
    if fs and exists is not None and not exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/touch", params={'filename': filename})
            except requests.exceptions.RequestException:
                continue

        fs.add_node(path=filename, is_dir=False, location=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/copy')
def copy():
    source = request.args.get('source')
    destination = request.args.get('destination')
    global fs
    response = 'Failed'
    exists = fs.file_exists(source)
    # if File System is initialized and source file exists
    if fs and exists is not None and not exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/copy",
                                        params={'source': source, 'destination': destination})
            except requests.exceptions.RequestException:
                continue

        fs.add_node(path=destination, is_dir=False, location=datanodes)

    return Response(status=200, response=response.content)


@app.route('/info')
def touch():
    # Get params
    filename = request.args.get('filename')

    # Create file if it does not exists
    global fs
    response = 'Failed'

    # True (exists), False (doesn't exist), or None (error)
    exists = fs.file_exists(filename)
    if fs and exists is not None and not exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/info", params={'filename': filename})
                break  # since we no need to get info about one file several times, one is enough
            except requests.exceptions.RequestException:
                continue
    return Response(status=200, response=response.content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True, use_reloader=False)
