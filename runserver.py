"""
This script runs the cloud_photo_gallery application using a development server.
"""

from os import environ
from cloud_photo_gallery import app
import sys

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        print('Attempt to run on', HOST,':', PORT)
    else:
        HOST = environ.get('SERVER_HOST', '0.0.0.0')
        try:
            PORT = int(environ.get('SERVER_PORT', '5000'))
            print('Attempt to run on', HOST,':', PORT)
        except ValueError:
            PORT = 5000

    print('Running on', HOST,':', PORT)
    app.run(HOST, PORT)

