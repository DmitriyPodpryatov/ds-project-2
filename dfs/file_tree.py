import random
import requests


class FileTree:
    class Node:
        def __init__(self, name: str, is_dir: bool, parent=None, children: dict = {},
                     location: list = None):
            self.children = children
            self.parent = parent
            self.name = name
            self.is_dir = is_dir
            self.location = location

    def __init__(self):
        self.root = FileTree.Node('/', True, children={})

    def search_node(self, path: str):
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
        current_node.children.update({directories[-1]: FileTree.Node(directories[-1], is_dir, parent=current_node,
                                                                     children={}, location=location)})

    def ls(self, path: str):
        if path == "/":
            result = {}
            for node in self.root.children:
                name = node
                d = self.root.children[node].is_dir
                result.__setitem__(name, d)
            return result
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node is not None:
            result = {}
            for node in current_node.children:
                name = node
                d = current_node.children[node].is_dir
                result.__setitem__(name, d)
            return result
        else:
            return None

    def update_location(self, path: str, location: str):
        paths = path.split('/')[1:]
        current_node = self.root
        for p in paths:
            current_node = current_node.children.get(p)
        current_node.location.append(location)

    def directory_exists(self, path: str):
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
