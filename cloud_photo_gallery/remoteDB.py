from cloud_photo_gallery import app
from psycopg2 import sql, connect
from psycopg2.extras import DictCursor

class remoteDB(object):
    """description of class"""

    def __init__(self):
        self.connection = remoteDB.connect()

    @staticmethod
    def connect():
        return connect(app.config['DB_URL'], sslmode='require')

    def close(self):
        if self.connection and not self.connection.closed : #returns 0 is open
            self.connection.close()

    def __del__(self):
        self.close()

#########################################
###           Init database           ###
#########################################

    @staticmethod
    def initialize():
        query(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {};")
                .format(sql.Identifier(app.config['PHOTO_SCHEMA']))
            )
        query(
            sql.SQL("""CREATE TABLE IF NOT EXISTS {}.{} (
                    id serial primary key,
                    username text not null UNIQUE,
                    password text not null
                    );""")
                .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(app.config['USERS_TABLE']))
            )


def query(query, vars=None) :
    db = remoteDB()
    with db.connection as conn:
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                print("\n",query.as_string(cursor) if hasattr(query, "as_string") else query, "\n")  #debug print
                cursor.execute(query, vars)
                print(cursor.statusmessage)  #debug print
                result = cursor.fetchall() if cursor.rowcount > 0 else None
            conn.commit()
            return result
        except Exception as e:
            print(e)
            conn.rollback()

