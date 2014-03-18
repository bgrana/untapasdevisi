# -*- coding: utf-8 -*-

import os
import utils

import redis

from flask import Flask, request, render_template, redirect, url_for, abort, flash
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
    if not current_user.validated:
        flash("Su cuenta de email aun no ha sido validada.", "warning")
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
    # expirar en 24h
    redis.expire('validate:key:'+ key, 60*60*24)

    utils.send_validation_email(user, key)

    login_user(user)
    return redirect(url_for('get_index'))


@app.route('/forgot_password', methods=['GET'])
def get_forgot_password():
    return render_template('forgot_password.html')


@app.route('/forgot_password', methods=['POST'])
def post_forgot_password():
    username = request.form['username']
    user = User.get_by_username(username)
    if user:
        key = utils.generate_key()
        redis.set('reset:key:'+ key, user.id)
        # expirar en 24h
        redis.expire('reset:key:'+ key, 60*60*24)
        # TODO: Arreglar caracteres unicode en templates
        utils.sent_reset_password_email(user, key)
        flash('Email de recuperacion de contrasena enviado correctamente.', 'success')
        return redirect(url_for('get_login'))
    else:
        # TODO: mostrar error
        return render_template('forgot_password.html')


@app.route('/reset_password', methods=['GET'])
def get_reset_password():
    key = request.args.get('key')
    userid = redis.get('reset:key:' + key)
    if not userid:
        abort(404)
    return render_template('reset_password.html')


@app.route('/reset_password', methods=['POST'])
def post_reset_password():
    key = request.args.get('key')
    password = request.form['password']

    if not password:
        return render_template('reset_password.html')

    userid = redis.get('reset:key:' + key)
    if not userid:
        abort(404)

    user = User.get(userid)
    user.update_password(password)
    redis.delete('reset:key:' + key)

    flash("Password actualizado correctamente.", 'success')
    return redirect(url_for('get_login'))


@app.route('/logout')
@login_required
def get_logout():
    logout_user()
    return redirect(url_for('get_login'))


@app.route('/validate', methods=['GET'])
def get_validate(username):
    key = request.args.get('key')

    userid = redis.get('validate:key:' + key)
    if not userid:
        abort(404)

    user = User.get(userid)
    user.validate()
    flash("Usuario validado correctamente.", 'success')
    return redirect(url_for('get_login'))


# ERROR HANDLERS
###############################################################################

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()