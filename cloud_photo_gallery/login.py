
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from cloud_photo_gallery import app
from urllib import parse
from os import makedirs
from os.path import exists, join
import pickle


class ID:
    value = 0
    map = {}

    @staticmethod
    def next(username):
        ID.value += 1
        val = ID.value
        ID.map[val] = username
        return val


# silly user model
class User(UserMixin):

    users = {}
    password = ''

    def __init__(self , name , password, active=True):
        self.id = ID.next(name)
        self.name = name
        self.password = password
        self.active = active

        
    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_auth_token(self):
        return make_secure_token(self.name , key=app.config.get('SECRET_KEY', None))

    def __repr__(self):
        return '%d/%s/%s' % (self.id, self.name, self.password)
    
    @staticmethod
    def save(user):
        User.users[user.name] = user
        if not exists(app.config['USERS_DEST']):
            makedirs(app.config['USERS_DEST'])
        with open(join(app.config['USERS_DEST'], app.config['USERS_FILE']), 'wb') as f:
            pickle.dump( User.users, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        with open(join(app.config['USERS_DEST'], app.config['USERS_FILE']), 'rb') as f:
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

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Logged in'
anon = login_manager.anonymous_user
anon.name = 'default'
login_manager.anonymous_user = anon
#app.config['TESTING'] = True
login_manager.init_app(app)


##########################################################################
##########################################################################
##########################################################################


def redirect_next(request):
    next_redirect = request.args.get('next')
    if next_redirect != None and next_redirect != '/':
        next_redirect = next_redirect.lstrip('/')
    else:
        next_redirect = 'home'
    print('redirect to', next_redirect)
    return redirect(next_redirect)      #url_for(next_redirect) #?

def get_next_redirect_string(request):
    next_redirect = request.args.get('next')
    if(next_redirect == None or next_redirect == ''):
        return ''
    return '?'+ parse.urlencode({'next':next_redirect})




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = False
        if request.form.get("remember") is not None:
            remember = request.form.get("remember") == 'on'
        print('login attempt for', username) #debug print
        if password == '' or password == None:
            return render_template(
                'login.html',
                title='Sign in',
                year=datetime.now().year,
                message='Sign in',
                login_error='password must not be empty',
                logged = current_user.is_authenticated,
                next_redirect = get_next_redirect_string(request)
            )

        if(User.users.get(username) == None):
            return render_template(
                'login.html',
                title='Sign in',
                year=datetime.now().year,
                message='Sign in',
                login_error='User name or password are incorrect',
                logged = current_user.is_authenticated,
                next_redirect = get_next_redirect_string(request)
            )

        user = User.users[username]
        if(password != user.password):
            return render_template(
                'login.html',
                title='Sign in',
                year=datetime.now().year,
                message='Sign in',
                login_error='User name or password are incorrect',
                logged = current_user.is_authenticated,
                next_redirect = get_next_redirect_string(request)
            )
        if login_user(user, remember = remember):
            #current_user = user
            print('Successful login for user: {id=', user.id, ', name=', user.name,'}') #debug print
        return redirect_next(request)
    else:
        return render_template(
            'login.html',
            title='Sign in',
            year=datetime.now().year,
            message='Sign in',
            logged = current_user.is_authenticated,
            next_redirect = get_next_redirect_string(request)
        )



@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    remember = False
    if request.form.get("remember") is not None:
        remember = request.form.get("remember") == 'on'
    if password != '' and password != None:
        if(User.users.get(username) != None):
                return render_template(
                    'login.html',
                    title='Sign in',
                    year=datetime.now().year,
                    message='Registering',
                    signup_error='User already exists',
                    logged = current_user.is_authenticated,
                    next_redirect = get_next_redirect_string(request)
                )
        user = User(username, password)
        User.save(user)
        print('New user: {id=', user.id, ', name=', user.name, '}') #debug print
        if login_user(user, remember = remember):
            #current_user = user
            print('Successful login for user: {id=', user.id, ', name=', user.name,'}') #debug print
        return redirect_next(request)
    else:
        return render_template(
            'login.html',
            title='Sign in',
            year=datetime.now().year,
            message='Registering',
            signup_error='password must not be empty',
            logged = current_user.is_authenticated,
            next_redirect = get_next_redirect_string(request)
        )




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



@login_manager.user_loader
def load_user(id):
    return User.users.get(ID.map.get(id))
    