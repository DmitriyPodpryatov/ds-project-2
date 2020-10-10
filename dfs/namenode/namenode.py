from flask import Flask, Response, request
from flask_cors import CORS
import requests


def valid_path(path: str):
    """
    Add root '/' at the beginning if it is not present

    :param path: path to file
    :return: path with root '/' at the beginning
    """
    if path[0] != '/':
        path = '/' + path

    return path


class FileSystem:
    """
    Keep track of file system in the namenode
    """

    def __init__(self):
        """
        Initialize root folder

        Set current directory to root (for `cd`)
        """
        self.root = FileSystem.File('/', is_dir=True, children={})
        self.current_dir = self.root

    class File:
        """
        Nested class for files in file system
        """

        def __init__(self, name: str, is_dir: bool, parent=None, children=None, location: [] = None):
            """
            Create file

            :param name: absolute path
            :param is_dir: directory flag
            :param parent: parent directory
            :param children: list of children files
            :param location: list of datanodes where this file is present
            """
            if children is None:
                children = {}

            self.name = name
            self.children = children
            self.parent = parent
            self.is_dir = is_dir
            self.location = location

    def set_current_dir(self, path):
        """
        Change current directory (for `cd`)

        :param path: new current directory
        """
        if path == '/':
            # Handle case with root directory
            self.current_dir = self.root
        else:
            # Find directory and set as a current
            self.current_dir = self.get_node(path)

    def get_node(self, path: str):
        """
        Get node by path

        :param path: absolute path to node
        :return: File
        """
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.current_dir

        for dir in directories:
            current_node = current_node.children.get(dir)

        return current_node

    def has_children(self, path):
        """
        Check if a directory has children

        :param path: absolute path to directory
        :return: whether a directory has children or not
        """
        if self.dir_exists(path):
            node = self.get_node(path)

            if len(node.children):
                return True
            else:
                return False

    def add_node(self, path: str, is_dir: bool, location: list):
        """
        Add node to the file system

        :param path: absolute path of a node
        :param is_dir: directory flag
        :param location: list of datanodes where this node is present
        """
        path = valid_path(path)

        directories = path.split('/')[1:]
        current_node = self.current_dir

        # path == '/' => root
        if not directories[0] == '':
            for dir in directories[:-1]:
                current_node = current_node.children.get(dir)

        # Add node
        new_node = FileSystem.File(directories[-1], is_dir, parent=current_node, children={}, location=location)
        current_node.children.update({directories[-1]: new_node})

    def dir_exists(self, path: str):
        """
        Check whether a given directory exists or not

        :param path: absolute path to directory
        :return: whether a directory exists or not
        """
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.current_dir

        # path == '/' => root => is a directory
        if directories[0] == '':
            return True

        for dir in directories:
            current_node = current_node.children.get(dir)

        if current_node is not None and current_node.is_dir:
            return True
        else:
            return False

    def file_exists(self, path: str):
        """
        Check whether a given file exists or not

        :param path: absolute path to file
        :return: whether a file exists or not
        """
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.current_dir

        for dir in directories:
            try:
                current_node = current_node.children.get(dir)
            except AttributeError:
                # No children => wrong path. Need for `touch`
                return None

        if current_node is not None and not current_node.is_dir:
            return True
        else:
            return False

    def delete_node(self, path: str, all_datanodes):
        """
        Delete node from file system

        :param all_datanodes: all active datanodes
        :param path: absolute path to node
        """
        path = valid_path(path)

        directories = path.split("/")[1:]
        current_node = self.current_dir

        # walk down in order to get node to delete
        for dir in directories:
            current_node = current_node.children.get(dir)

        response = "Failed"
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

            # pop the deleted node from parent list of children
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

# List of datanodes IP:PORT
datanodes = ["10.0.15.11:7777", "10.0.15.12:7777", "10.0.15.13:7777"]

# File system
fs: FileSystem


@app.route('/hello')
def hello():
    """
    Check for active datanodes

    :return: Response with hello from itself and all active datanodes
    """
    res = "Hello from namenode!\n\n"

    # Ask all datanodes
    for datanode in datanodes:
        res += requests.get("http://" + datanode + "/hello").text + "\n"

    return Response(status=200, response=res)


@app.route('/init')
def init():
    """
    Clear DFS

    :return: Response with free space in MB
    """
    global fs
    fs = FileSystem()

    # Ask all datanodes for free space
    result = 0
    active_datanodes = 0
    for datanode in datanodes:
        try:
            response = requests.get("http://" + datanode + "/init")

            result += int(response.content)
            active_datanodes += 1
        except requests.exceptions.RequestException:
            continue

    # Divide total space by number of active datanodes
    try:
        storage = "The available storage is " + str(round(result // len(datanodes) / (1024 * 1024), 2)) + " MB"
    except ZeroDivisionError:
        storage = "The available storage is 0 MB"

    return Response(status=200, response=storage)


@app.route('/touch')
def touch():
    """
    Create empty file

    :return: Response with acknowledgement
    'Failed' if file system is not initialized, file already exists, or datanodes are not available
    """
    # Get file name
    filename = request.args.get('filename')

    global fs
    response = 'Failed'

    # True (exists), False (doesn't exist), or None (error)
    exists = fs.file_exists(filename)
    # Send request to all datanodes
    if fs and exists is not None and not exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/touch", params={'filename': filename})
            except requests.exceptions.RequestException:
                continue

        # Add file to file system
        fs.add_node(path=filename, is_dir=False, location=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/read')
def read():
    """
    Redirect client to datanode to read (download) a file

    :return: Response with datanode address
    'Failed' if file system is not initialized, file does not exist, or datanodes are not available
    """
    # Get file name
    filename = request.args.get('filename')
    filename = valid_path(filename)

    global fs
    response = 'Failed'

    file_exists = fs.file_exists(filename)
    if file_exists:
        # Get datanode with file
        datanode = fs.get_node(filename).location[0]
        return Response(status=200, response=datanode)
    else:
        return Response(status=200, response=response)


@app.route('/write')
def write():
    """
    Redirect client to datanodes to write (upload) a file

    :return: Response with string with datanode addresses
    'Failed' if file system is not initialized, destination folder does not exist, destination file already exists,
    or datanodes are not available
    """
    # Get file name and destination folder
    destination_dir = request.args.get('destination_dir')
    filename = valid_path(request.args.get('filename'))
    filename = filename[filename.rfind('/'):]

    global fs
    response = 'Failed'

    # dir exists but file must not exist
    dir_exists = fs.dir_exists(destination_dir)

    if destination_dir != '/':
        filename = destination_dir + filename
    file_exists = fs.file_exists(filename)

    global datanodes
    if dir_exists and not file_exists:
        # check case when we write to root directory, if we write to root, we write to all active datanodes
        # since, technically, root has no FileSystem object and therefore will not have location attribute
        if destination_dir == '/':
            nodes = '|'.join(datanodes)
            fs.add_node(filename, is_dir=False, location=datanodes)
        else:
            nodes = '|'.join(fs.get_node(destination_dir).location)
            fs.add_node(filename, is_dir=False, location=fs.get_node(destination_dir).location)
        return Response(status=200, response=nodes)
    else:
        return Response(status=200, response=response)


@app.route('/rm')
def rm():
    """
    Remove file

    :return: Response with acknowledgement
    'Failed' if file system is not initialized, file does not exist, or datanodes are not available
    """
    # Get file name
    filename = request.args.get('filename')

    global fs
    response = 'Failed'

    file_exists = fs.file_exists(filename)
    # Send request to all datanodes
    if fs is not None and file_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/rm", params={'filename': filename})
            except requests.exceptions.RequestException:
                continue

        # Remove file from file system
        fs.delete_node(path=filename, all_datanodes=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/info')
def info():
    """
    Show file info

    :return: Response with file info
    'Failed' if file system is not initialized, file does not exist, or datanodes are not available
    """
    # Get file name
    filename = request.args.get('filename')

    global fs
    response = 'Failed'

    file_exists = fs.file_exists(filename)
    # Send request to all datanodes
    if fs is not None and file_exists:
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


@app.route('/copy')
def copy():
    """
    Copy file

    :return: Response with acknowledgement
    'Failed' if file system is not initialized, file does not exist, destination folder does not exist,
    or datanodes are not available
    """
    # Get file name and destination folder
    source = request.args.get('source')
    destination = request.args.get('destination')

    global fs
    response = 'Failed'

    file_exists = fs.file_exists(source)
    dest_dir_exists = True
    # Get destination folder and whether it exists
    if destination.rfind('/') != -1 and destination.rfind('/') != 0:
        destination_dir = destination[0:destination.rfind('/')]
        dest_dir_exists = fs.dir_exists(destination_dir)

    # Send request to all datanodes
    if fs is not None and file_exists and dest_dir_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/copy",
                                        params={'source': source, 'destination': destination})
            except requests.exceptions.RequestException:
                continue

        # Add file to file system
        fs.add_node(path=destination, is_dir=False, location=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/move')
def move():
    """
    Move (cut and paste) file

    :return: Response with acknowledgement
    'Failed' if file system is not initialized, file already exists, or datanodes are not available
    """
    # Get file name and destination folder
    moving_file = request.args.get('filename')
    destination_dir = request.args.get('destination_dir')

    global fs
    response = 'Failed'

    file_exists = fs.file_exists(moving_file)
    dest_dir_exists = fs.dir_exists(destination_dir)
    # Send request to all datanodes
    if fs is not None and file_exists and dest_dir_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/move",
                                        params={'filename': moving_file, 'destination_dir': destination_dir})
            except requests.exceptions.RequestException:
                continue

        # Remove file from file system
        fs.delete_node(moving_file, all_datanodes=datanodes)

        temp_path = valid_path(moving_file)
        if destination_dir != '/':
            # Get new path
            new_filename = destination_dir + temp_path[temp_path.rfind('/'):]
        else:
            new_filename = temp_path[temp_path.rfind('/')+1:]
        # Add file to file system
        fs.add_node(new_filename, is_dir=False, location=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/cd')
def cd():
    """
    Change directory

    :return: Response with acknowledgement
    'Failed' if file system is not initialized, directory does not exist, or datanodes are not available
    """
    # Get folder name
    dirname = request.args.get('dirname')

    global fs
    response = 'Failed'

    dir_exists = fs.dir_exists(dirname)
    # Send request to all datanodes
    if fs is not None and dir_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/cd", params={'dirname': dirname})
            except requests.exceptions.RequestException:
                continue

        # Change file system's current directory
        fs.set_current_dir(dirname)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/ls')
def ls():
    """
    List files in directory

    :return: Response with string of files in directory
    'Failed' if file system is not initialized, directory does not exist, or datanodes are not available
    """
    # Get folder name
    dirname = request.args.get('dirname')

    global fs
    response = 'Failed'

    dir_exists = fs.dir_exists(dirname)
    # Send request to all datanodes
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
    """
    Create empty directory

    :return: Response with acknowledgement
    'Failed' if file system is not initialized, directory does not exist, or datanodes are not available
    """
    # Get folder name
    dirname = request.args.get('dirname')

    global fs
    response = 'Failed'

    dir_exists = fs.dir_exists(dirname)
    # Send request to all datanodes
    if fs is not None and not dir_exists:
        for datanode in datanodes:
            try:
                response = requests.get("http://" + datanode + "/mkdir", params={'dirname': dirname})
            except requests.exceptions.RequestException:
                continue

        # Add directory to file system
        fs.add_node(path=dirname, is_dir=True, location=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


@app.route('/rmdir')
def rmdir():
    """
    Remove directory. Ask for permission if directory is not empty

    :return:
    'Failed' if file system is not initialized, directory does not exist, or datanodes are not available
    """
    # Get params
    dirname = request.args.get('dirname')
    ack = request.args.get('ack')

    global fs
    response = 'Failed'

    dir_exists = fs.dir_exists(dirname)
    if fs is not None and dir_exists:
        # Folder is not empty and there is no acknowledgement from client => ask client for permission
        if fs.has_children(dirname) and ack is None:
            return Response(status=200, response='nonempty')

        # Either folder is empty or request has acknowledgement
        # Send request to all datanodes
        if not fs.has_children(dirname) or ack == 'y':
            for datanode in datanodes:
                try:
                    response = requests.get("http://" + datanode + "/rmdir", params={'dirname': dirname})
                except requests.exceptions.RequestException:
                    continue

            # Remove folder from file system
            fs.delete_node(path=dirname, all_datanodes=datanodes)

    if type(response) == str:
        # response == 'Failed'
        return Response(status=200, response=response)
    else:
        # response == Response object
        return Response(status=200, response=response.content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True, use_reloader=False)
