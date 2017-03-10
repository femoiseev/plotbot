from server import server
import os
from flask import Flask

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
    server = Flask(__name__)
