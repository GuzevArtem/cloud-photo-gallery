
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify, Response
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from cloud_photo_gallery import app
from cloud_photo_gallery.remoteDB import query
from psycopg2 import sql
from urllib import parse
from os import makedirs
from os.path import exists, join
import pickle


class ID:
    #last user id
    value = 0
    #id -> username
    map = {}

    @staticmethod
    def next(username):
        ID.value += 1
        val = ID.value
        ID.map[val] = username
        return val
    
    @staticmethod
    def put(id, name):
        ID.value = max(id,ID.value)
        ID.map[id] = name
        return id;


# silly user model
class User(UserMixin):
    db = None
    #username -> user
    users = {}
    password = ''

    def __init__(self , name , password, id = None, remember_me = False, active=True):
        self.id = ID.put(id, name) if id is not None else ID.next(name)
        self.name = name
        self.password = password
        self.active = active
        self.remember_me = remember_me

        
    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_remmber_me(self):
        return self.remember_me

    def get_auth_token(self):
        return make_secure_token(self.name , key=app.config.get('SECRET_KEY', None))

    def __repr__(self):
        return '%d/%s/%s' % (self.id, self.name, self.password)
    
    @staticmethod
    def save(user, to_db = True):
        if User.db and to_db:
            id = query(
                sql.SQL("""INSERT INTO {}.{} (id, username, password)
                        VALUES (DEFAULT,%s,%s)
                        ON CONFLICT DO NOTHING
                        RETURNING id;""")
                        .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(app.config['USERS_TABLE'])),
                        (user.name, user.password)
                    )
            user.id = id[0][0]
            ID.map[user.id] = user.name
            print('Saved user', user.name, 'with id:', user.id) #debug print
        User.users[user.name] = user
        if not exists(app.config['USERS_DEST']):
            makedirs(app.config['USERS_DEST'])
        with open(join(app.config['USERS_DEST'], app.config['USERS_FILE']), 'wb') as f:
            pickle.dump( User.users, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        rs = {}
        if User.db:
            rs = query(
                sql.SQL("""SELECT * FROM {}.{};""")
                .format(sql.Identifier(app.config['PHOTO_SCHEMA']), sql.Identifier(app.config['USERS_TABLE']))
                )
        if User.db and rs and len(rs) != 0:
            print('Loading',len(rs),'users from db') #debug print
            User.users = {}
            for rowUser in rs:
                user = User(id = rowUser[0], name = rowUser[1], password = rowUser[2])
                User.users[user.name] = user
            for username in User.users:
                User.save(User.users[username], False)
        else:
            print('loading users from local') #debug print
            local_users_dump = join(app.config['USERS_DEST'], app.config['USERS_FILE'])
            if(exists(local_users_dump)):
                with open(local_users_dump, 'rb') as f:
                    User.users = pickle.load(f)
                    for username in User.users:
                        user = User.users[username]
                        ID.map[user.id] = username
                        ID.value = max(ID.value, user.id)
        return User.users




##########################################################################
############################## config ####################################
##########################################################################
app.config.update(
    #DEBUG = True,
    SECRET_KEY = 'xxx_secret_xxx'
)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Logged in'
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
anon = login_manager.anonymous_user
anon.name = 'default'
login_manager.anonymous_user = anon
#app.config['TESTING'] = True
login_manager.init_app(app)


@app.before_request
def pre_request():
    #if True - session will expire after time
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=31) if isinstance(current_user._get_current_object(), login_manager.anonymous_user) or current_user.is_remmber_me() else timedelta(minutes=5)
    session.modified = True



@login_manager.user_loader
def load_user(id):
    return User.users.get(ID.map.get(id))
    
##########################################################################
##########################################################################
##########################################################################


def redirect_next(request):
    next_redirect = request.args.get('next')
    if next_redirect != None and next_redirect != '/':
        next_redirect = next_redirect.lstrip('/')
    else:
        next_redirect = 'home'
    print('redirect to', next_redirect) #debug print
    return redirect(next_redirect)

def redirect_string_next(request):
    next_redirect = request.args.get('next')
    if next_redirect != None and next_redirect != '/':
        next_redirect = next_redirect.lstrip('/')
    else:
        next_redirect = 'home'
    next_redirect = request.host_url + next_redirect
    print('redirect to', next_redirect) #debug print
    return next_redirect

def get_next_redirect_string(request):
    next_redirect = request.args.get('next')
    if(next_redirect == None or next_redirect == ''):
        return ''
    return '?'+ parse.urlencode({'next':next_redirect})



@app.route('/login', methods=['GET'])
def loginPage():
    return render_template(
            'login.html',
            title='Sign in',
            year=datetime.now().year,
            message='Sign in',
            logged = current_user.is_authenticated,
            next_redirect = get_next_redirect_string(request)
        )

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        abort(400)

    req = request.get_json() 
    print(req) #debug print
    username = req.get('username')
    password = req.get('password')
    remember = False
    if req.get("remember") is not None:
        remember = (req.get("remember") == 'on')
    print('login attempt for', username, "remember", remember) #debug print
    if password == '' or password == None:
        return 
        return jsonify({'error_msg':'password must not be empty'}) , 400
    User.load()
    if(User.users.get(username) == None):
        return jsonify({'error_msg':'User name or password are incorrect'}) , 400

    user = User.users[username]
    if(password != user.password):
        return jsonify({'error_msg':'User name or password are incorrect'}) , 400
    user.remember_me = remember
    user.active = True
    if login_user(user, remember = remember):
        #current_user = user
        print('Successful login for user: {id=', user.id, ', name=', user.name,'}') #debug print
    return jsonify({'href':redirect_string_next(request)}), 200




@app.route('/signup', methods=['POST'])
def signup():
    if not request.is_json:
        abort(400)

    req = request.get_json() 
    print(req) #debug print
    username = req.get('username')
    password = req.get('password')
    remember = False
    if req.get("remember") is not None:
        remember = (req.get("remember") == 'on')
    if password != '' and password != None:
        User.load()
        if(User.users.get(username) != None):
            return jsonify({'error_msg':'User already exists'}) , 400

        user = User(id = -1, name = username, password = password, remember_me = remember)
        User.save(user)
        print('New user: {id=', user.id, ', name=', user.name, '}') #debug print
        if login_user(user, remember = remember):
            #current_user = user
            print('Successful login for user: {id=', user.id, ', name=', user.name,'}') #debug print
        return jsonify({'href':redirect_string_next(request)}), 204
    else:
        return jsonify({'error_msg':'Password must not be empty'}) , 400



@app.route('/logout')
@login_required
def logout():
    if not isinstance(current_user._get_current_object(), login_manager.anonymous_user):
        if not isinstance(current_user._get_current_object(), login_manager.anonymous_user):
            current_user._get_current_object().active = False
    logout_user()
    return redirect(url_for('home'))
