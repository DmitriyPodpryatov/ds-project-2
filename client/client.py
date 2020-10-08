import sys
import requests
import os

namenode = "10.0.15.10:5555"


def request(s: str, params=None, show=True):
    if params is None:
        params = {}

    try:
        # https://requests.readthedocs.io/en/master/user/quickstart/
        result = requests.get(f'http://{namenode}/' + s, params=params)

        if show:
            print(result.text)


    except Exception as e:
        print(e)


def print_help():
    print("""\nList of available commands:
    hello - just hello
    init - initialize and prepare DFS. Return available size
    touch FILE - create empty file FILE
    """)


def read_file():
    pass


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

        else:
            print("Incorrect command!\nFor help write command: help")


if __name__ == '__main__':
    main()
