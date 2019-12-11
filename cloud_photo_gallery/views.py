"""
Routes and views for the flask application.
"""

from os import path
from datetime import datetime
from urllib import parse
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, send_file, send_from_directory
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from cloud_photo_gallery import app
from cloud_photo_gallery.photo_holder import photo_holder, Photo



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


@app.route('/photo/<id>/remove')
@login_required
def photoRemove(id):
    try:
        username = current_user.name
        photo_holder.remove(username, int(id))
        return redirect(url_for('photos'))
    except FileNotFoundError:
        abort(404) 

@app.route('/photo/<username>/<id>/download')
@login_required
def photoDownload(username, id):
    """Returns the photo."""
    try:
        photos = photo_holder.get_photos_for(username)
        if photos is not None:
            photo = photos.get(int(id))
            if photo is not None:
                return send_file(photo.get_full_path(), mimetype=photo.content_type, as_attachment=True, attachment_filename=photo.name)
        abort(401)
    except FileNotFoundError:
        abort(404) 

@app.route('/photo/<username>/<id>/show') #not used. Use uploadSet instead
@login_required
def photoShow(username, id):
    """Returns the photo."""
    try:
        photo = photo_holder.get_photo_for(username, int(id))
        if photo is not None:
            return send_from_directory(photo.filepath, photo.get_full_name(), mimetype=photo.content_type)
        abort(401)
    except FileNotFoundError:
        abort(404) 


@app.route('/photos')
@login_required
def photos():
    """Renders the photos page."""
    photos = photo_holder.get_photos_for(current_user.name)
    print('Draw photos for', current_user.name ,':', photos ) #debug print
    if photos is not None:
        if len(photos) != 0:
            images = []
            for id in photos:
                file = photos[id]
                images.append({
                    'id': file.id,
                    'filename': file.name,
                    'height': 250,
                    'url': file.url
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
    return render_template(
        'list_photo.html',
        title='Photo',
        year=datetime.now().year,
        message='List your photos.',
        logged = current_user.is_authenticated
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
