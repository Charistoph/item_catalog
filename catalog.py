# -*- coding: utf-8 -*-
from flask import Flask, render_template, g, request, redirect, jsonify, url_for, flash, abort, make_response
from flask import session as login_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import relationship, sessionmaker
from findARestaurant import findARestaurant
from database_setup import Base, Advert, User
import random, string, sys, codecs
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from redis import Redis
import time
from functools import update_wrapper

# old
#app = Flask(__name__)


from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
# allow http transport
# (https requires ssl keys, not good for local testing)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# init flask app
app = Flask(__name__)

# default values
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set database uri for SQLAlchemy
if os.environ.get('DB_URI') is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
        + os.path.join(basedir, '../database.sqlite3')

app.config['CSRF_ENABLED'] = True
app.secret_key = 'no one can guess this'
# enable debug for auto reloads
app.debug = True

# login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

# database
db = SQLAlchemy(app)



# old

#CLIENT_ID = json.loads(
#    open('client_secrets.json', 'r').read())['web']['client_id']
#APPLICATION_NAME = "Meet N' Greet"
#
#
## Connect to Database and create database session
#engine = create_engine('sqlite:///catalog.db')
#Base.metadata.bind = engine
#
#DBSession = sessionmaker(bind=engine)
#session = DBSession()
#
#
##-------------------------------------------------------------------------------
# Rate Limiting Class & Decorator
# START redis-server for this to work!!
#
#redis = Redis()
#
## Check redis-server status
#try:
#    response = redis.client_list()
#    print "Status: redis-server running!"
#except redis.ConnectionError:
#    print "ERROR: redis-server not running! Use redis-server in bash!"
#
#class RateLimit(object):
#    expiration_window = 10
#
#    def __init__(self, key_prefix, limit, per, send_x_headers):
#        self.reset = (int(time.time()) // per) * per + per
#        self.key = key_prefix + str(self.reset)
#        self.limit = limit
#        self.per = per
#        self.send_x_headers = send_x_headers
#        p = redis.pipeline()
#        p.incr(self.key)
#        p.expireat(self.key, self.reset + self.expiration_window)
#        self.current = min(p.execute()[0], limit)
#
#    remaining = property(lambda x: x.limit - x.current)
#    over_limit = property(lambda x: x.current >= x.limit)
#

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)


def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


#-------------------------------------------------------------------------------
# Login Code

# Create anti-forgery state token
@app.route('/login')
@ratelimit(limit=300, per=30 * 1)
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
@ratelimit(limit=300, per=30 * 1)
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
#    request.get_data()
#    code = request.data.decode('utf-8')
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
@ratelimit(limit=300, per=30 * 1)
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#-------------------------------------------------------------------------------
# Advert Code

# Show all adverts
@app.route('/')
@app.route('/advert/')
@ratelimit(limit=300, per=30 * 1)
def showAdverts():
    adverts = session.query(Advert).order_by(asc(Advert.name))
    if 'username' not in login_session:
        return render_template('publicadverts.html', adverts=adverts)
    else:
        return render_template('adverts.html', adverts=adverts, user_id_session=login_session['user_id'], user_name_session=login_session['username'])

# Create a new advert


@app.route('/advert/new/', methods=['GET', 'POST'])
@ratelimit(limit=300, per=30 * 1)
def newAdvert():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
#        newAdvert = Advert(
#            name=request.form['name'], user_id=login_session['user_id'])
        newAdvert = Advert(location=request.form['location'], meal_type=request.form['meal_type'], meal_time=request.form['meal_time'])
#    location = request.args.get('location', '')
#    meal_type = request.args.get('meal_type', '')
#    meal_time = request.args.get('meal_time', '')
        advert_info = findARestaurant(newAdvert.meal_type, newAdvert.location)
        if advert_info != "No Restaurants Found":
            newAdvert = Advert(address = unicode(advert_info['address']), name = unicode(advert_info['name']), meal_type = newAdvert.meal_type, meal_time = newAdvert.meal_time, user_id = login_session['user_id'], creator = login_session['username'], attendee = "None yet!", accept_attendee = "No")
            session.add(newAdvert)
            flash('New Proposal %s Successfully Created' % newAdvert.name)
            session.commit()
            return redirect(url_for('showAdverts'))
    else:
        return render_template('newAdvert.html')

# Edit a advert
@app.route('/advert/<int:advert_id>/edit/', methods=['GET', 'POST'])
@ratelimit(limit=300, per=30 * 1)
def editAdvert(advert_id):
    editedAdvert = session.query(
        Advert).filter_by(id=advert_id).one()
    deleteAdvert = session.query(
        Advert).filter_by(id=advert_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedAdvert.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this advert. Please create your own advert in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['location']:
            editedAdvert.location = request.form['location']
        if request.form['meal_type']:
            editedAdvert.meal_type = request.form['meal_type']
        if request.form['meal_time']:
            editedAdvert.meal_time = request.form['meal_time']
        advert_info = findARestaurant(editedAdvert.meal_type, editedAdvert.location)
        if advert_info != "No Restaurants Found":
            editedAdvert = Advert(address = unicode(advert_info['address']), name = unicode(advert_info['name']), meal_type = editedAdvert.meal_type, meal_time = editedAdvert.meal_time, user_id = login_session['user_id'], creator = login_session['username'])
        session.add(editedAdvert)
        session.commit()
        session.delete(deleteAdvert)
        session.commit()
        flash('Advert Successfully Edited')
        return redirect(url_for('showAdverts'))
    else:
        return render_template('editAdvert.html', advert=editedAdvert)


# Delete a advert
@app.route('/advert/<int:advert_id>/delete/', methods=['GET', 'POST'])
@ratelimit(limit=300, per=30 * 1)
def deleteAdvert(advert_id):
    advertToDelete = session.query(
        Advert).filter_by(id=advert_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if advertToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this advert. Please create your own advert in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(advertToDelete)
        flash('%s Successfully Deleted' % advertToDelete.name)
        session.commit()
        return redirect(url_for('showAdverts', advert_id=advert_id))
    else:
        return render_template('deleteAdvert.html', advert=advertToDelete)


# Join a advert
@app.route('/advert/<int:advert_id>/join/', methods=['GET', 'POST'])
@ratelimit(limit=300, per=30 * 1)
def joinAdvert(advert_id):
    editedAdvert = session.query(
        Advert).filter_by(id=advert_id).one()
    deleteAdvert = session.query(
        Advert).filter_by(id=advert_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    # not really needed, just for safety.
    if editedAdvert.user_id == login_session['user_id']:
        return "<script>function myFunction() {alert('You cannot join your own proposal');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        editedAdvert.attendee = login_session['username']
        session.add(editedAdvert)
        session.commit()
        flash('Advert Successfully Edited')
        return redirect(url_for('showAdverts'))
    else:
        return render_template('joinAdvert.html', advert=editedAdvert)


# Accept a join proposal
@app.route('/advert/<int:advert_id>/accept/', methods=['GET', 'POST'])
@ratelimit(limit=300, per=30 * 1)
def acceptAdvert(advert_id):
    editedAdvert = session.query(
        Advert).filter_by(id=advert_id).one()
    deleteAdvert = session.query(
        Advert).filter_by(id=advert_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    # not really needed, just for safety.
    if editedAdvert.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You cannot accept this proposal');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        editedAdvert.accept_attendee = "Yes"
        session.add(editedAdvert)
        session.commit()
        flash('Advert Successfully Accepted')
        return redirect(url_for('showAdverts'))
    else:
        return render_template('joinAdvert.html', advert=editedAdvert)


#-------------------------------------------------------------------------------
# Main

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
# Test APIs
#    findARestaurant("Pizza", "Tokyo, Japan")
