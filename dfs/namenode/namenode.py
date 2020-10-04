import json

import requests

datanodes = []

from http.server import HTTPServer
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs

from http.server import BaseHTTPRequestHandler


class HttpHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def message(self, args):
        msg = {'msg': 'success'}

        if self.path == '/hello':
            msg['msg'] = "Well, hello hello, young lady!"
        else:
            print("Error! Command doesn't exist.")
            msg['msg'] = 'failure'

        return msg

    def do_GET(self):


        # I spent 2+ hours thinking why http response does not have field 'Content-length' and DIDN'T succeed

        # content_length = int(self.headers['Content-length'])
        # post_data = self.rfile.read(content_length)
        # args = json.loads(post_data)

        # soo я закостылил
        # upd оно не будет работать для команд с 2+ аргументами
        a = self.requestline
        args = a[4:a.index("HTTP") - 1]
        print(args)

        # in case if we call from browser, to avoid get command for ico
        if args.endswith(".ico"):
            self._set_response()
            return

        try:
            msg = self.message(args)
            self._set_response()
            self.wfile.write(json.dumps(msg).encode('utf-8'))  # send message back to the sender
        except ConnectionResetError:
            pass



def main():
    # Create an object of the above class
    handler_object = HttpHandler

    PORT = 80
    my_server = HTTPServer(("0.0.0.0", PORT), handler_object)
    my_server.serve_forever()


if __name__ == '__main__':
    main()
