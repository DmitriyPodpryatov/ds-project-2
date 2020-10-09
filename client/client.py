import sys
import requests


namenode = "10.0.15.10:5555"


def request(s: str, params=None, show=True, download=False, upload=False):
    if params is None:
        params = {}

    try:
        # https://requests.readthedocs.io/en/master/user/quickstart/
        result = requests.get(f'http://{namenode}/' + s, params=params)
        if download and result.text != 'Failed':
            data = requests.get(f'http://{result.text}/' + s, params=params).content
            filename = params['filename']
            downloaded_file = open(filename, "wb")
            downloaded_file.write(bytes(data))
            print(f"File {filename} is successfully downloaded.")
        elif upload and result.text != 'Failed':
            filename = params['filename']
            with open(filename, 'rb') as fp:
                data = fp.read()
            params = {'filename': params['filename'], 'destination_dir': params['destination_dir'], "data": data}
            datanodes = result.text.split("|")
            response = "Failed"
            for datanode in datanodes:
                response = requests.get(f'http://{datanode}/' + s, params=params)
            if type(response) == str:
                print(response)
            else:
                print(response.content)
        elif show:
            print(result.text)

    except Exception as e:
        print(e)


def print_help():
    print("""\nList of available commands:
    hello - just hello
    init - initialize and prepare DFS. Return available size
    touch FILE - create empty file FILE
    """)


def main():
    # Get args
    args = sys.argv[1:]

    if len(args) == 0:
        print("Empty command!")

    elif len(args) == 1:
        if args[0] == 'help':
            print_help()

        elif args[0] == 'hello':
            request('hello')

        elif args[0] == 'init':
            request('init')
        else:
            print("Incorrect command!\nFor help write command: help")

    elif len(args) == 2:
        # Create file
        if args[0] == 'touch':
            request('touch', params={'filename': args[1].encode()})

        elif args[0] == 'ls':
            request('ls', params={'dirname': args[1].encode()})

        elif args[0] == 'mkdir':
            request('mkdir', params={'dirname': args[1].encode()})

        elif args[0] == 'info':
            request('info', params={'filename': args[1].encode()})

        elif args[0] == 'read':
            request('read', params={'filename': args[1].encode()}, download=True)

        elif args[0] == 'rm':
            request('rm', params={'filename': args[1].encode()})

        elif args[0] == 'rmdir':
            with requests.Session() as session:
                response = session.get(f'http://{namenode}/rmdir', params={'dirname': args[1].encode()})

                if response.text == 'nonempty':
                    ack = input('rmdir: do you want to remove nonempty directory? [y/N] ')

                    if ack == 'y':
                        result = session.get(f'http://{namenode}/rmdir', params={'dirname': args[1].encode(), 'ack': 'y'})
                        print(result.text)
                else:
                    print(response.text)

        else:
            print("Incorrect command!\nFor help write command: help")
    elif len(args) == 3:
        if args[0] == 'copy':
            request('copy', params={'source': args[1].encode(), 'destination': args[2].encode()})

        elif args[0] == 'move':
            request('move', params={'filename': args[1].encode(), 'destination_dir': args[2].encode()})
        elif args[0] == 'write':
            request('write', params={'filename': args[1].encode(), 'destination_dir': args[2].encode()}, upload=True, show=False)

        else:
            print("Incorrect command!\nFor help write command: help")


if __name__ == '__main__':
    main()
