"""
The flask application package.
"""

from flask import Flask, url_for
from os import listdir, getcwd
from os.path import isfile, join, exists
from urllib import parse
from PIL import Image

app = Flask(__name__)
app.config['img_folder'] = 'user_images'
app.config['UPLOADED_PHOTOS_DEST'] = join(getcwd(), app.config['img_folder'])
app.config['USERS_DEST'] = join(getcwd(), 'users')
app.config['USERS_FILE'] = 'users.pkl'

import cloud_photo_gallery.login as l
import cloud_photo_gallery.views as v
import cloud_photo_gallery.photo_holder as ph

try:
    users = l.User.load()

    for username in users:
        user = users[username]
        photos = []
        path = join(app.config['UPLOADED_PHOTOS_DEST'], username)
        if exists(path):
            onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
            for filename in onlyfiles:
                with Image.open(join(path,filename)) as file:
                    with app.app_context(), app.test_request_context():
                        url = url_for('photoShow', username = username, photoname = filename)
                        photos.append(ph.Photo(filename , url, path, Image.MIME[file.format]))
            print('Saving photos for', username, ':', photos) #debug print
            ph.photo_holder.add_photos_for(username, photos)
except FileNotFoundError:
    pass

