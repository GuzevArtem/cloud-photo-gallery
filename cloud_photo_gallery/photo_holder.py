import io
import os
from cloud_photo_gallery.remoteDB import query
from psycopg2 import sql, Binary
from cloud_photo_gallery import app
from flask import url_for

class Photo(object):
    """description of class"""

    def __init__(self, id = None, name = None, url = None, filepath = None, content_type = None):
        self.id = id if id is not None else ID.next()
        self.url = url
        self.filepath = filepath
        self.content_type = content_type
        self.name, self.extension = os.path.splitext(name)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name+self.extension

    def get_full_path(self):
        return os.path.join(self.filepath, self.get_full_name())

    def get_full_name(self):
        return str(self.id)+'.'+self.getName()

    def __str__(self):
        return 'Photo(id=%d, name=/%s, filepath=%s, url=/%s)' % (self.id, self.getName(), self.filepath, self.url)

    def __repr__(self):
        return str(self)

class ID:
    def __init__(self, value = 0):
        self.value = value

    def cur(self):
        return self.value

    def next(self):
        self.value = self.value+1
        return self.value



class photo_holder(object):
    """description of class"""

    #username -> ID object
    IDs = {}

    @staticmethod
    def get_next_photo_id(username):
        ids = photo_holder.IDs.get(username)
        if ids:
            return ids.next()
        else: #id - default id, usually 0
            id = ID()
            photo_holder.IDs[username] = id
            return id.cur();

    @staticmethod
    def override_photo_id(username, value):
        photo_holder.IDs[username] = ID(value)
        return value



    db = None

    #username -> photo_id -> photo_object
    photo_storage = {}
      
    @staticmethod
    def _create_photo_dict_for(username):
        photo_holder.photo_storage[username] = {}
        photo_holder.IDs[username] = ID()
        if photo_holder.db: query(
            sql.SQL("""CREATE TABLE IF NOT EXISTS {}.{} (
                    id serial primary key,
                    filename text not null,
                    url text not null,
                    content_type text not null,
                    image bytea not null
                    );""")
                .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(username))
            )



    @staticmethod
    def create_photo_dict_for(username):
        if photo_holder.photo_storage.get(username) == None:
            photo_holder._create_photo_dict_for(username)



    @staticmethod
    def _add_photos_for(username, photos):
        if photo_holder.photo_storage.get(username) == None:
            photo_holder._create_photo_dict_for(username)
        for photo in photos:
            photo_holder.photo_storage[username][photo.id] = photo



    @staticmethod
    def add_photos_for(username, photos):
        for photo in photos:
            with open(photo.get_full_path(), 'rb') as file:
                if photo_holder.db: 
                    id = query(
                        sql.SQL("""INSERT INTO {}.{} (id, filename, url, content_type, image)
                        VALUES (""" + (str(photo.id) if photo.id else 'DEFAULT') + """,%s,%s,%s,%s)
                        RETURNING id;
                        """)
                        .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(username)),
                        [photo.getName(), photo.url, photo.content_type, Binary(file.read())]
                        )
                    photo.id = id[0][0]
                else:
                    photo.id = photo_holder.get_next_photo_id(username)
                print("Saved photo with id:",id,"for", username)  #debug print
        photo_holder._add_photos_for(username, photos)
        return photos


    @staticmethod
    def gen_next_id(username):
        id = photo_holder.get_next_photo_id(username)
        try:
            id = int(file.filename.split('.',2)[0])
        except:
            rs = None
            if photo_holder.db:
                rs = query(
                    sql.SQL("""SELECT nextval(pg_get_serial_sequence({},'id'));""")
                        .format(sql.Literal(app.config['PHOTO_SCHEMA']+'.'+username))
                    )
            if rs:
                id = photo_holder.override_photo_id(username, int(rs[0][0]))
        return id

    @staticmethod
    def save_photos_for(username, files):
        if len(files) != 0:
            path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], username)
            if not os.path.exists(path):
                os.makedirs(path)
            photo_holder.create_photo_dict_for(username)
            photos = []
            for file in files:
                id = photo_holder.gen_next_id(username)
                print("Next id:",id)  #debug print
                url = url_for('photoShowFor', username = username, id = id)
                photos.append(Photo(id = id, name = file.filename , url = url, filepath = path, content_type = file.content_type))
            for i in range(len(files)):
                files[i].save(photos[i].get_full_path())
                print("Saved photo locally with id:",photos[i].id,"for", username,'at',photos[i].get_full_path())  #debug print
            photos = photo_holder.add_photos_for(username, photos)



    @staticmethod
    def get_photos_for(username):
        result = {}
        cached = photo_holder.photo_storage.get(username)
        if cached is not None and len(cached) != 0 and all(os.path.exists(cached[id].get_full_path()) for id in cached):
            result = dict(cached.items())
        elif photo_holder.db:
            photo_holder.create_photo_dict_for(username)
            dbRows = query(
                            sql.SQL("""SELECT * FROM  {}.{};""")
                                .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(username))
                        )
            if dbRows:
                for row in dbRows:
                    photo = Photo(row[0], row[1], row[2], os.path.join(app.config['UPLOADED_PHOTOS_DEST'], username), row[3])
                    if not os.path.exists(photo.filepath):
                        os.makedirs(photo.filepath)
                    with open(photo.get_full_path(),'wb') as f:
                        f.write(bytes(row[4]))
                    print("Loaded photo", photo.getName(),"id",photo.id,"for",username,"photo:",photo) #debug print
                    result[photo.id] = photo
        photo_holder._add_photos_for(username, list(result.values()))
        return result

    @staticmethod
    def get_photos_ids_for(username):
        result = []
        cached = photo_holder.photo_storage.get(username)
        if photo_holder.db:
            dbRows = query(
                            sql.SQL("""SELECT id FROM  {}.{};""")
                                .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(username))
                        )
            if dbRows:
                for row in dbRows:
                    result.append(row[0])
        elif cached is not None and len(cached) != 0 and all(os.path.exists(cached[id].get_full_path()) for id in cached):
            result.append(list(cached.keys()))
        return result

    @staticmethod
    def get_photo_for(username, photo_id):
        cached = photo_holder.photo_storage.get(username)
        if cached is not None and len(cached) != 0 and cached.get(photo_id) is not None:
            return cached.get(photo_id)
        else:
            return photo_holder.get_photos_for(username).get(photo_id)


    @staticmethod
    def rename(username, id, name):
        photos = photo_holder.photo_storage.get(username)
        if photos is not None:
            photo = photos.get(id)
            if photo is not None:
                oldPath = photo.get_full_path()
                photo.setName(name)
                os.rename(oldPath, photo.get_full_path())
                print('File renamed for', username, ':', photo.id,':', photo.getName()) #debug print
        if photo_holder.db:
            result = query(
                    sql.SQL("""UPDATE {}.{}
                    SET filename = {}
                    WHERE id = %s RETURNING id;""")
                    .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(username), sql.Literal(name)),
                    [id]
                    )
            print("Updated",result[0][0],"for",username) #debug print



    @staticmethod
    def remove(username, id):
        photos = photo_holder.photo_storage.get(username)
        if photos is not None:
            photo = photos.get(id)
            if photo is not None:
                os.remove(photo.get_full_path())
                print('File removed for', username, ':', photo.id,':', photo.getName()) #debug print
                photos.pop(id)
        if photo_holder.db:
            result = query(
                    sql.SQL("""DELETE FROM {}.{} WHERE id = %s RETURNING id;""")
                    .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(username)),
                    [id]
                    )
            print("Deleted",result[0][0],"for",username) #debug print
