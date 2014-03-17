# -*- coding: utf-8 -*-

import os
import utils

import redis

from flask import Flask, request, render_template, redirect, url_for, abort
from flask.ext.login import LoginManager, login_user, current_user, login_required, logout_user

from models import db, User

# Setup
###############################################################################

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update({
    'DEBUG': True,
    'SECRET_KEY': os.getenv('UNTAPASDEVISI_SECRET_KEY', 'development_key'),
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/untapasdevisi_dev.db',
    'REDIS_URL': 'localhost'
})

redis = redis.from_url(app.config['REDIS_URL'])

db.init_app(app)
db.create_all(app=app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('get_login'))


# Routes
###############################################################################

@app.route('/', methods=['GET'])
@login_required
def get_index():
    return render_template('index.html', username=current_user.username)


@app.route('/login', methods=['GET'])
def get_login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def post_login():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return render_template('login.html', error=True)

    user = User.authenticate(username, password)

    if not user:
        return render_template('login.html', error=True)

    login_user(user)
    return redirect(url_for('get_index'))


@app.route('/register', methods=['GET'])
def get_register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def post_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if not username or not password or not email:
        return render_template('register.html', error=True)

    user = User.register(username, password, email)

    if not user:
        return render_template('register.html', error=True)

    key = utils.generate_key()
    redis.set('validate:key:'+ key, user.id)
    utils.send_validation_email(email, key)

    login_user(user)
    return redirect(url_for('get_index'))


@app.route('/logout')
@login_required
def get_logout():
    logout_user()
    return redirect(url_for('get_login'))


@app.route('/keys/<key>', methods=['GET'])
def get_key(key):
    userid = redis.get('validate:key:' + key)
    if not userid:
        abort(404)

    user = User.get(userid)
    user.validate()

    return redirect(url_for('get_login'))


# ERROR HANDLERS
###############################################################################

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()