"""
Routes and views for the flask application.
"""

from os import path
from datetime import datetime
from urllib import parse
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, send_file, send_from_directory, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from cloud_photo_gallery import app
from cloud_photo_gallery.photo_holder import photo_holder, Photo
from hashlib import sha512

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        logged=current_user.is_authenticated
    )



@app.route('/share/upload', methods=['POST'])
@login_required
def share_upload():
    files = request.files.getlist("file[]")
    print('recieved:', files)
    photo_holder.save_photos_for(current_user.name, files)
    return redirect(url_for('share'))



@app.route('/share')
@login_required
def share():
    """Renders the share page."""
    return render_template(
        'share_photo.html',
        title='Share photo',
        year=datetime.now().year,
        message='Share your photos.',
        logged = current_user.is_authenticated
    )



@app.route('/photo/<id>', methods = ['DELETE'])
@login_required
def photoRemove(id):
    try:
        username = current_user.name
        photo_holder.remove(username, int(id))
        return jsonify(status='Deleted'), 200
    except FileNotFoundError:
        abort(404) 



@app.route('/photo/<username>/<id>/download', methods = ['GET'])
@login_required
def photoDownload(username, id):
    """Returns the photo."""
    try:
        photos = photo_holder.get_photos_for(username)
        if photos is not None:
            photo = photos.get(int(id))
            if photo is not None:
                return send_file(photo.get_full_path(), mimetype=photo.content_type, as_attachment=True, attachment_filename=photo.getName())
        abort(401)
    except FileNotFoundError:
        abort(404) 



@app.route('/photo/<username>/<id>', methods = ['GET'])
@login_required
def photoShowFor(username, id):
    """Returns the photo."""
    try:
        photo = photo_holder.get_photo_for(username, int(id))
        if photo is not None:
            return send_from_directory(photo.filepath, photo.get_full_name(), mimetype=photo.content_type)
        abort(400)
    except FileNotFoundError:
        abort(404) 



@app.route('/photo/<id>', methods = ['GET'])
@login_required
def photoShow(id):
    return photoShowFor(current_user.name, id)



@app.route('/photo/<id>', methods = ['PUT'])
@login_required
def photoUpdate(id):
    if not request.is_json:
        abort(400)
    req = request.get_json()
    name = req.get('name')
    if not name or len(name) == 0:
        abort(400)
    try:
        photo_holder.rename(current_user.name, int(id), name)
        return jsonify(status='Updated'), 200
    except:
        abort(404)
            


@app.route('/photos/reload/', methods = ['POST'])
@login_required
def check_reload():
    if not request.is_json:
        abort(400)

    req = request.get_json()
    count = req.get('count')
    hash = req.get('hash')

    ids = photo_holder.get_photos_ids_for(current_user.name)
    if count != len(ids):
        return get_reload_photos()
    ids.sort()
    string = str(ids)
    string = string.replace(" ", "").replace("[","").replace("]","")
    #print('ids in db:',string) #debug print
    calculatedHash = sha512(bytearray(string,'ascii'))
    print(count, hash, calculatedHash.hexdigest()) #debug print
    return get_reload_photos() if hash != str(calculatedHash.hexdigest()) else jsonify([])



@app.route('/photos/reload', methods = ['GET'])
@login_required
def get_reload_photos():
    photos = photo_holder.get_photos_for(current_user.name)
    print('Draw photos for', current_user.name ,':', photos ) #debug print
    images = []
    if photos is not None:
        if len(photos) != 0:
            for id in photos:
                photo = photos[id]
                images.append({
                    'id': photo.id,
                    'filename': photo.getName(),
                    'height': 250,
                    'url': photo.url,
                    'removeUrl': url_for('photoRemove', id = id),
                    'downloadUrl': url_for('photoDownload', username = current_user.name, id = id)
                })
            print('Viewing', images) #debug print images = []
    return jsonify(images), 200



@app.route('/photos', methods = ['GET'])
@login_required
def photos():
    """Renders the photos page."""
    photos = photo_holder.get_photos_for(current_user.name)
    print('Draw photos for', current_user.name ,':', photos ) #debug print
    images = []
    if photos is not None:
        if len(photos) != 0:
            for id in photos:
                photo = photos[id]
                images.append({
                    'id': photo.id,
                    'filename': photo.getName(),
                    'height': 250,
                    'url': photo.url
                })
            print('Viewing', images) #debug print
    return render_template(
        'list_photo.html',
        title='Photo',
        year=datetime.now().year,
        message='List your photos.',
        logged = current_user.is_authenticated,
        **{'images': images}
    )



@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.',
        logged = current_user.is_authenticated
    )



@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.',
        logged = current_user.is_authenticated
    )
