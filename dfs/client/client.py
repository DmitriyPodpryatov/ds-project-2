import sys
import requests
import os

namenode = '0.0.0.0'


def request(s: str, args='', show=True):
    try:
        result = requests.get(f'http://{namenode}:8080/' + s, json=args)
        if show:
            print(result.json()['msg'])
        return result.json()['msg']
    except Exception as e:
        print(e)


def print_help():
    print("""\nList of available commands:
    hello - just hello
    """)


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Empty command!")
    elif len(args) == 1:
        if args[0] == 'help':
            print_help()
        elif args[0] == 'hello':
            request('hello')
        else:
            print("Incorrect command!\nFor help write command: help")


if __name__ == '__main__':
    main()
