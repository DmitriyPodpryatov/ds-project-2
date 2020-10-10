import os
import shutil
import subprocess
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Driver root
base_path = '/dfs'


@app.route('/hello')
def hello():
    """
    Say hello

    :return: Response with hello
    """
    return Response(status=200, response="Hello from datanode!")


@app.route('/init')
def init():
    """
    Clear file system

    :return: free space in bytes
    """
    os.system('rm -rf ' + base_path + "/*")
    total, used, free = shutil.disk_usage('/')
    return Response(status=200, response=str(free))


@app.route('/touch')
def touch():
    """
    Create empty file

    :return: Response with acknowledgement
    """
    # Get filename
    filename = request.args.get('filename')
    os.system('touch ' + base_path + '/' + filename)
    return Response(status=200, response=f'File {filename} was created.')


@app.route('/read', methods=['GET', 'POST'])
def read():
    """
    Send file (upload)

    :return: Response with file content
    """
    # Get file name
    filename = base_path + '/' + request.args.get('filename')

    # Read data and send it
    with open(filename, 'rb') as fp:
        data = fp.read()

    return Response(status=200, response=data)


@app.route('/write', methods=['GET', 'POST'])
def write():
    """
    Receive file (download)

    :return: Response with acknowledgement
    """
    # Get file name and destination folder
    filename = request.args.get('filename')
    destination_dir = request.args.get('destination_dir')

    # Add root '/' if it is not present
    if filename[0] != '/':
        filename = '/' + filename

    # Get '/filename' out of absolute path
    filename = filename[filename.rfind('/'):]
    # Construct new absolute path relative to root folder
    filename = destination_dir + filename
    # Construct absolute path relative to the host
    filename = base_path + '/' + filename

    # Read data and write it to the file
    data = request.args.get('data')
    file = open(filename, "wb")
    file.write(data.encode())

    return Response(status=200, response=f"The data is put into dfs.")


@app.route('/rm')
def rm():
    """
    Remove file

    :return: Response with acknowledgement
    """
    # Get file name
    filename = request.args.get('filename')
    os.system('rm ' + base_path + '/' + filename)
    return Response(status=200, response=f'File {filename} was deleted.')


@app.route('/info')
def info():
    """
    Show file info

    :return: Response with file info
    """
    # Get file name
    filename = request.args.get('filename')
    # Construct absolute path relative to root folder
    filename = base_path + '/' + filename

    # Run `stat filename` in the OS and save the output
    proc = subprocess.Popen(['stat ' + filename], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if not err:
        response = "The information:\n" + out.decode()
    else:
        response = err

    return Response(status=200, response=response)


@app.route('/copy')
def copy():
    """
    Copy file

    :return: Response with acknowledgement
    """
    # Get source file and destination folder
    source = request.args.get('source')
    destination = request.args.get('destination')
    os.system('cp ' + base_path + '/' + source + ' ' + base_path + '/' + destination)
    return Response(status=200, response=f'Copy of file {source} was created at {destination}')


@app.route('/move')
def move():
    """
    Move (cut and paste) file

    :return: Response with acknowledgement
    """
    # Get source file and destination folder
    filename = request.args.get('filename')
    destination_dir = request.args.get('destination_dir')
    os.system('mv ' + base_path + '/' + filename + " " + base_path + '/' + destination_dir)
    return Response(status=200, response=f'File {filename} was moved to directory {destination_dir}.')


@app.route('/cd')
def cd():
    """
    Change directory

    :return: Response with acknowledgement
    """
    # Get dir name
    dirname = request.args.get('dirname')

    # Change "root" dir
    global base_path
    base_path = '/dfs' + '/' + dirname

    return Response(status=200, response=f'Changed directory to {dirname}')


@app.route('/ls')
def ls():
    """
    List files in directory

    :return: Response with string of files in directory
    """
    # Get dir name and list of files in it
    dirname = request.args.get('dirname')
    files = os.listdir(base_path + '/' + dirname)

    # Return string with files separated by tab
    response = ''
    for file in files:
        response += file + '\t'

    return Response(status=200, response=response)


@app.route('/mkdir')
def mkdir():
    """
    Create empty directory

    :return: Response with acknowledgement
    """
    # Get dir name
    dirname = request.args.get('dirname')
    os.system('mkdir ' + base_path + '/' + dirname)
    return Response(status=200, response=f'Directory {dirname} was created.')


@app.route('/rmdir')
def rmdir():
    """
    Remove directory

    :return: Response with acknowledgement
    """
    # Get dir name
    dirname = request.args.get('dirname')
    os.system('rm -rf ' + base_path + '/' + dirname)
    return Response(status=200, response=f'Directory {dirname} was deleted.')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
