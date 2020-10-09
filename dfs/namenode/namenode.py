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

    def get_node(self, path: str):
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)

        return current_node

    def find_node(self, path: str):
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None:
            return current_node.location
        return []

    def has_children(self, path):
        if self.dir_exists(path):
            node = self.get_node(path)

            if len(node.children):
                return True
            else:
                return False

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

    def delete_node(self, path: str, all_datanodes):
        path = valid_path(path)
        directories = path.split("/")[1:]
        current_node = self.root
        response = "Failed"
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None:
            if not current_node.is_dir:
                datanodes = current_node.location
                for datanode in datanodes:
                    if current_node.is_dir:
                        try:
                            response = requests.get("http://" + datanode + "/rmdir", params={'dirname': path})
                        except requests.exceptions.RequestException:
                            pass

                    else:
                        try:
                            response = requests.get("http://" + datanode + "/rm", params={'filename': path})
                        except requests.exceptions.RequestException:
                            pass
            else:
                for datanode in all_datanodes:
                    if current_node.is_dir:
                        try:
                            response = requests.get("http://" + datanode + "/rmdir", params={'dirname': path})
                        except requests.exceptions.RequestException:
                            pass

                    else:
                        try:
                            response = requests.get("http://" + datanode + "/rm", params={'filename': path})
                        except requests.exceptions.RequestException:
                            pass
            current_node.parent.children.pop(current_node.name)

            if type(response) == str:
                # response == 'Failed'
                return Response(status=200, response=response)
            else:
                # response == Response object
                return Response(status=200, response=response.content)
        else:
            return Response(status=200, response=response)


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


@app.route('/ls')
def ls():
    # Get params
    dirname = request.args.get('dirname')

    global fs
    response = 'Failed'

    dir_exists = fs.dir_exists(dirname)
    if fs is not None and dir_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/ls", params={'dirname': dirname})
            except requests.exceptions.RequestException:
                continue

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/mkdir')
def mkdir():
    # Get params
    dirname = request.args.get('dirname')

    # Create file if it does not exists
    global fs
    response = 'Failed'

    # True (exists), False (doesn't exist), or None (error)
    exists = fs.dir_exists(dirname)

    if fs and exists is not None and not exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/mkdir", params={'dirname': dirname})
            except requests.exceptions.RequestException:
                continue

        fs.add_node(path=dirname, is_dir=True, location=datanodes)

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
    file_exists = fs.file_exists(source)
    dest_dir_exists = True
    if destination.rfind('/') != -1 and destination.rfind('/') != 0:
        destination_dir = destination[0:destination.rfind('/')]
        dest_dir_exists = fs.dir_exists(destination_dir)

    # if File System is initialized and source file exists and destination directory exists
    if fs is not None and file_exists and dest_dir_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/copy",
                                        params={'source': source, 'destination': destination})
            except requests.exceptions.RequestException:
                continue

        fs.add_node(path=destination, is_dir=False, location=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/rm')
def rm():
    # Get params
    filename = request.args.get('filename')

    # Create file if it does not exists
    global fs
    response = 'Failed'

    # True (exists), False (doesn't exist), or None (error)
    file_exists = fs.file_exists(filename)
    if fs is not None and file_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/rm", params={'filename': filename})
            except requests.exceptions.RequestException:
                continue

        fs.delete_node(path=filename, all_datanodes=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/rmdir')
def rmdir():
    # Get params
    dirname = request.args.get('dirname')
    ack = request.args.get('ack')

    # Create file if it does not exists
    global fs
    response = 'Failed'

    dir_exists = fs.dir_exists(dirname)
    if fs is not None and dir_exists:
        if fs.has_children(dirname):
            return Response(status=200, response='nonempty')

        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/rmdir", params={'dirname': dirname})
            except requests.exceptions.RequestException:
                continue

        fs.delete_node(path=dirname, all_datanodes=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


# @app.route('/move')
# def move():
#     moving_file = request.args.get('filename')
#     destination_dir = request.args.get('destination_dir')
#     global fs
#     response = 'Failed'
#     file_exists = fs.file_exists(moving_file)
#     dest_dir_exists = fs.dir_exists(destination_dir)
#
#     # if File System is initialized and source file exists and destination directory exists
#     if fs is not None and file_exists and dest_dir_exists:
#         for datanode in datanodes:
#             try:
#                 response = requests.get("http://" + datanode + "/move",
#                                         params={'filename': moving_file, 'destination_dir': destination_dir})
#             except requests.exceptions.RequestException:
#                 continue
#
#
#     if type(response) == str:
#         # response == 'Failed'
#         return Response(status=200, response=response)
#     else:
#         # response == Response object
#         return Response(status=200, response=response.content)
#

@app.route('/info')
def info():
    # Get params
    filename = request.args.get('filename')

    # Create file if it does not exists
    global fs
    response = 'Failed'

    exists = fs.file_exists(filename)

    if fs is not None and exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/info", params={'filename': filename})
            except requests.exceptions.RequestException:
                continue

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True, use_reloader=False)
