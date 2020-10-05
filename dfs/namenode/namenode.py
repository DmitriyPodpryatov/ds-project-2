from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json


class FileSystem:
    def __init__(self):
        self.root = FileSystem.File('/', is_dir=True, child={})

    class File:
        def __init__(self, name: str, is_dir: bool, parent=None, child: dict = {},
                     location: [] = None):
            self.name = name
            self.child = child
            self.parent = parent
            self.is_dir = is_dir
            self.location = location

    def find_node(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None:
            return current_node.location
        return []

    def add_node(self, path: str, is_dir: bool, location: list):
        directories = path.split('/')[1:]
        current_node = self.root
        for dir in directories[:-1]:
            current_node = current_node.children.get(dir)
        new_node = FileSystem.File(directories[-1], is_dir, parent=current_node, child={}, location=location)
        current_node.children.update({directories[-1]: new_node})

    def update_location(self, path: str, location: str):
        directories = path.split('/')[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        current_node.location.append(location)

    def dir_exists(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None and current_node.is_dir == True:
            return True
        else:
            return False

    def file_exists(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None and current_node.is_dir == False:
            return True
        else:
            return False


app = Flask(__name__)
CORS(app)
datanodes = ["10.0.15.11:7777", "10.0.15.12:7777", "10.0.15.13:7777"]


@app.route('/hello')
def hello():
    res = "Hello from namenode!\n\n"
    for datanode in datanodes:
        res += requests.get("http://" + datanode + "/hello").text + "\n"
    return Response(status=200, response=res)


@app.route('/init')
def init():
    fs = FileSystem()
    result = 0
    for datanode in datanodes:
        try:
            response = requests.get("http://" + datanode + "/init")
        except requests.exceptions.RequestException:
            continue
        result += int(response.content.decode())
    storage = "The available storage is " + str(result // 3)
    return Response(status=200, response=storage)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True, use_reloader=False)
