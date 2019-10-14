class Photo(object):
    """description of class"""

    def __init__(self, name, url, filepath, content_type):
        self.name = name
        self.url = url
        self.filepath = filepath
        self.content_type = content_type


class photo_holder(object):
    """description of class"""

    photo_storage = {}


    def __init__():
       photo_holder.create_photo_dict_for('default')
       
    def create_photo_dict_for(username):
        photo_holder.photo_storage[username] = {}

    def add_photos_for(username, photos):
        if photo_holder.photo_storage.get(username) == None:
            photo_holder.create_photo_dict_for(username)
        for photo in photos:
            photo_holder.photo_storage[username][photo.name] = photo

    def get_photos_for(username):
        return photo_holder.photo_storage.get(username)
