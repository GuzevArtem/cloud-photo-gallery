from cloud_photo_gallery import app
from psycopg2 import connect
from psycopg2.extras import DictCursor

class remoteDB(object):
    """description of class"""

    def __init__(self):
        self.connection = remoteDB.connect()

    @staticmethod
    def connect():
        return connect(app.config['DB_URL'], sslmode='require')

    def close(self):
        if not self.connection.closed : #returns 0 is open
            self.connection.close()

    def __del__(self):
        self.close()

#########################################
###           Init database           ###
#########################################

    @staticmethod
    def initialize():
        query("CREATE SCHEMA IF NOT EXISTS photos")

@staticmethod
def query(query, vars=None) :
    db = remoteDB()
    with db.connection as conn:
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, vars)
                cursor.commit()
            conn.commit()
            return cursor.fetchall()
        except:
            conn.rollback()
        finally:
            db.close()

