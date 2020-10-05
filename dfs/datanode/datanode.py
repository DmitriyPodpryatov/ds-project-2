from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)


@app.route('/hello')
def hello():
    return Response(status=200, response="Hello from datanode!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
