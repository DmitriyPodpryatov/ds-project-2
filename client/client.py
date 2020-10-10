import sys
import requests

# Namenode IP and port
namenode = "10.0.15.10:5555"


def request(s: str, params=None, show=True, download=False, upload=False):
    """
    Send command to namenode

    :param s: command
    :param params: additional parameters
    :param show: print response
    :param download: download flag
    :param upload: upload flag
    """
    if params is None:
        params = {}

    try:
        # Create HTTP request
        # https://requests.readthedocs.io/en/master/user/quickstart/
        result = requests.get(f'http://{namenode}/' + s, params=params)

        # Download file
        if download and result.text != 'Failed':

            data = requests.get(f'http://{result.text}/' + s, params=params).text

            # Get file name
            filename = params['filename']

            # Create file and write into it from DFS
            downloaded_file = open(filename, "wb")
            downloaded_file.write(bytes(data))

            print(f"File {filename} is successfully downloaded.")

        # Upload file
        elif upload and result.text != 'Failed':
            # Get file name
            filename = params['filename']

            # Read file and send its content to DFS
            with open(filename, 'rb') as fp:
                data = fp.read()

            # Set file name, destination folder, and file's content
            params = {'filename': params['filename'], 'destination_dir': params['destination_dir'], "data": data}

            # Get list of datanodes
            datanodes = result.text.split("|")

            # Send file to datanodes
            response = "Failed"
            for datanode in datanodes:
                response = requests.get(f'http://{datanode}/' + s, params=params)

            if type(response) == str:
                print(response)
            else:
                print(response.text)

        elif show:
            print(result.text)

    except Exception as e:
        print(e)


def print_help():
    print("""\nList of available commands:
    
    hello - say hello
    init - initialize and prepare DFS. Return available size
    touch FILE - create empty FILE
    read FILE - download FILE
    write FILE DEST_DIR - upload FILE into DEST_DIR
    rm FILE - remove FILE
    info FILE - show info about FILE
    copy SOURCE DEST - copy SOURCE into DEST
    move FILE DEST_DIR - move FILE into DEST_DIR
    cd DIR - open DIR
    ls DIR - list of files in DIR
    mkdir DIR - create DIR
    rmdir DIR - remove DIR
    
    Note: use `/` for the root folder. No `.` or `..` are allowed. No trailing `/` are allowed
    """)


def incorrect_command():
    print("Incorrect command!\nFor help run: help")


def main():
    # Get args
    args = sys.argv[1:]

    if len(args) == 0:
        print("Empty command!\nFor help write command: help")

    elif len(args) == 1:
        if args[0] == 'help':
            print_help()

        elif args[0] == 'hello':
            request('hello')

        elif args[0] == 'init':
            request('init')
        else:
            incorrect_command()

    elif len(args) == 2:
        # Create file
        if args[0] == 'touch':
            request('touch', params={'filename': args[1].encode()})

        # Download file
        elif args[0] == 'read':
            request('read', params={'filename': args[1].encode()}, download=True)

        # Remove file
        elif args[0] == 'rm':
            request('rm', params={'filename': args[1].encode()})

        # Show file info
        elif args[0] == 'info':
            request('info', params={'filename': args[1].encode()})

        # Open directory
        elif args[0] == 'cd':
            request('cd', params={'dirname': args[1].encode()})

        # List files in directory
        elif args[0] == 'ls':
            request('ls', params={'dirname': args[1].encode()})

        # Create directory
        elif args[0] == 'mkdir':
            request('mkdir', params={'dirname': args[1].encode()})

        # Remove directory
        elif args[0] == 'rmdir':
            # Create session
            with requests.Session() as session:
                response = session.get(f'http://{namenode}/rmdir', params={'dirname': args[1].encode()})

                # If directory is not empty, ask user for permission to delete it
                if response.text == 'nonempty':
                    # Get acknowledgement
                    ack = input('rmdir: do you want to remove nonempty directory? [y/N] ')

                    # Approved? => Delete folder
                    if ack == 'y':
                        result = session.get(f'http://{namenode}/rmdir',
                                             params={'dirname': args[1].encode(), 'ack': 'y'})
                        print(result.text)
                else:
                    print(response.text)

        else:
            incorrect_command()

    elif len(args) == 3:
        # Upload file
        if args[0] == 'write':
            request('write', params={'filename': args[1].encode(), 'destination_dir': args[2].encode()}, upload=True,
                    show=False)

        # Copy file
        elif args[0] == 'copy':
            request('copy', params={'source': args[1].encode(), 'destination': args[2].encode()})

        # Move file
        elif args[0] == 'move':
            request('move', params={'filename': args[1].encode(), 'destination_dir': args[2].encode()})

        else:
            incorrect_command()

    else:
        incorrect_command()


if __name__ == '__main__':
    main()
