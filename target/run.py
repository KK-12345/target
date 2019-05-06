import sys
import os

from flup.server.fcgi import WSGIServer

from target.settings import app

if __name__ == '__main__':
    WSGIServer(app).run()

