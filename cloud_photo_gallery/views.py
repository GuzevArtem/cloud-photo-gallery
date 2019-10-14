"""
Routes and views for the flask application.
"""

import io
import os
from datetime import datetime
from urllib import parse
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, send_file, send_from_directory
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from cloud_photo_gallery import app
from cloud_photo_gallery.photo_holder import photo_holder, Photo


uploadPhotos = UploadSet('photos', IMAGES)
configure_uploads(app, uploadPhotos)
patch_request_class(app)  # set maximum file size, default is 16MB

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
    photos = []
    for file in files:
        #filename = uploadPhotos.save(       ##############uploadPhotos
        #        file,
        #        name=file.filename    
        #    )
        path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], current_user.name)
        if not os.path.exists(path):
            os.makedirs(path)
        url = parse.urljoin(request.host_url, url_for('photoShow', username = current_user.name, photoname = file.filename))
        file.save(os.path.join(path, file.filename))
        photos.append(Photo(file.filename , url, path, file.content_type))
    print('Saving photos for', current_user.name, ':', photos) #debug print
    photo_holder.add_photos_for(current_user.name, photos)
    return redirect(url_for('share'));



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


@app.route('/photo/<photoname>/remove')
@login_required
def photoRemove(photoname):
    try:
        username = current_user.name
        photos = photo_holder.get_photos_for(username)
        if photos is not None:
            photo = photos.get(photoname)
            if photo is not None:
                photos.pop(photoname)
                os.remove(os.path.join(photo.filepath, photo.name))
                print('File removed for', username, ':', photo.name) #debug print
        return redirect(url_for('photos'))
    except FileNotFoundError:
        abort(404) 

@app.route('/photo/<username>/<photoname>/download')
@login_required
def photoDownload(username, photoname):
    """Returns the photo."""
    try:
        photos = photo_holder.get_photos_for(username)
        if photos is not None:
            photo = photos.get(photoname)
            if photo is not None:
                return send_file(os.path.join(photo.filepath, photo.name), mimetype=photo.content_type, as_attachment=True, attachment_filename=photo.name)
        abort(401)
    except FileNotFoundError:
        abort(404) 

@app.route('/photo/<username>/<photoname>/show') #not used. Use uploadSet instead
@login_required
def photoShow(username, photoname):
    """Returns the photo."""
    try:
        photos = photo_holder.get_photos_for(username)
        if photos is not None:
            image = photos.get(photoname)
            if image is not None:
                return send_from_directory(image.filepath, image.name, mimetype=image.content_type)
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
            for filename in photos:
                file = photos[filename]
                images.append({
                    'height': 250,
                    'filename': file.name,
                    'url': uploadPhotos.url(current_user.name+'/'+file.name)
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
