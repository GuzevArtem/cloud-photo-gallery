import io
import os
from cloud_photo_gallery.remoteDB import query
from psycopg2 import sql, Binary
from cloud_photo_gallery import app


class Photo(object):
    """description of class"""

    def __init__(self, id = None, name = None, url = None, filepath = None, content_type = None):
        self.id = id
        self.name = name
        self.url = url
        self.filepath = filepath
        self.content_type = content_type


class photo_holder(object):
    """description of class"""

    db = None

    photo_storage = {}
      
    @staticmethod
    def create_photo_dict_for(username):
        photo_holder.photo_storage[username] = {}
        if photo_holder.db: query(
            sql.SQL("""CREATE TABLE IF NOT EXISTS {} (
                    id serial primary key,
                    filename text not null UNIQUE,
                    url text not null,
                    content_type text not null,
                    image bytea not null
                    );""")
                .format(sql.Identifier(username))
            )

    @staticmethod
    def _add_photos_for(username, photos):
        if photo_holder.photo_storage.get(username) == None:
            photo_holder.create_photo_dict_for(username)
        for photo in photos:
            photo_holder.photo_storage[username][photo.name] = photo

    @staticmethod
    def add_photos_for(username, photos):
        photo_holder._add_photos_for(username, photos)
        for photo in photos:
            with open(os.path.join(photo.filepath, photo.name), 'rb') as file:
                if photo_holder.db: 
                    id = query(
                        sql.SQL("""INSERT INTO {} (id, filename, url, content_type, image)
                        VALUES (DEFAULT,%s,%s,%s,%s)
                        RETURNING id;
                        """)
                        #ON CONFLICT ON CONSTRAINT {}
                        #DO UPDATE SET filename=EXCLUDED.filename||'_'
                        .format(sql.Identifier(username), sql.Identifier(username+"_filename_key")),
                        [photo.name, photo.url, photo.content_type, Binary(file.read())]
                        )
                    photo.id = id[0][0]
                print("Saved photo with id:",id,"for", username)  #debug print

    @staticmethod
    def get_photos_for(username):
        result = {}
        cached = photo_holder.photo_storage.get(username)
        if cached is not None and len(cached) != 0 and all(os.path.exists(os.path.join(cached[photoname].filepath, cached[photoname].name)) for photoname in cached):
            result = dict(cached.items())
        elif photo_holder.db:
            photo_holder.create_photo_dict_for(username)
            dbRows = query(
                            sql.SQL("""SELECT * FROM  {};""")
                                .format(sql.Identifier(username))
                        )
            if dbRows:
                for row in dbRows:
                    photo = Photo(row[0], row[1], row[2], os.path.join(app.config['UPLOADED_PHOTOS_DEST'], username), row[3])
                    if not os.path.exists(photo.filepath):
                        os.makedirs(photo.filepath)
                    with open(os.path.join(photo.filepath, photo.name),'wb') as f:
                        f.write(bytes(row[4]))
                    print("Loaded photo", photo.name,"for",username,"photo:",photo) #debug print
                    result[photo.name] = photo
        photo_holder._add_photos_for(username, list(result.values()))
        return result


    @staticmethod
    def remove(username, photoname):
        photos = photo_holder.photo_storage.get(username)
        if photos is not None:
            photo = photos.get(photoname)
            if photo is not None:
                os.remove(os.path.join(photo.filepath, photo.name))
                print('File removed for', username, ':', photo.name) #debug print
                photos.pop(photoname)
        if photo_holder.db: result = query(
                    sql.SQL("""DELETE FROM {} WHERE filename like %s RETURNING id;""")
                    .format(sql.Identifier(username)),
                    [photoname]
                    )
        print("Deleted",result,"for",username)
