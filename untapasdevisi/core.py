# -*- coding: utf-8 -*-

import utils
from bson import json_util
import datetime

import redis

from babel.dates import format_date, format_timedelta

from flask import Flask, request, render_template, redirect, url_for
from flask import abort, flash, jsonify
from flask.ext.login import LoginManager, login_user, current_user
from flask.ext.login import login_required, logout_user

from models import User, Friendship, Activity, Local, connect_db
from forms import ProfileForm, RegisterForm, LoginForm, LocalForm

# Setup
###############################################################################

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update({
    'DEBUG': True,
    'SECRET_KEY': 'development_key',
    'HOST': '127.0.0.1:5000',
    'MAILGUN_API_USER': 'sandbox74944',
    'MAILGUN_API_KEY': 'key-84mxu54004c5y47zgym0z-d34jnsvl18',
    'MONGODB_DB_NAME': 'untapasdevisi',
    'REDIS_URL': 'localhost'
})

mailer = utils.Mailer(
    app.config['MAILGUN_API_USER'],
    app.config['MAILGUN_API_KEY'],
    app.config['HOST']
)

redis = redis.from_url(app.config['REDIS_URL'])

connect_db(app.config['MONGODB_DB_NAME'])

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return User.objects(id=userid).first()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('get_login'))

# Filters
###############################################################################


@app.template_filter('date')
def date_filter(date):
    return format_date(date, format='long', locale='es')


@app.template_filter('ago')
def ago_filter(date):
    delta = datetime.datetime.now() - date
    return format_timedelta(delta, locale='es')

# Routes
###############################################################################


@app.route('/', methods=['GET'])
@login_required
def get_index():
    friends = Friendship.get_confirmed_from_user(current_user)
    return render_template('index.html', user=current_user, friends=friends)


@app.route('/configuracion', methods=['GET'])
@login_required
def get_settings():
    data = {
        "username": current_user.username,
        "email": current_user.email,
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
        "location": current_user.location
    }
    form = ProfileForm(**data)
    return render_template('settings.html', user=current_user, form=form)


@app.route('/configuracion', methods=['POST'])
@login_required
def post_settings():
    form = ProfileForm(request.form)
    if form.validate():
        current_user.update(form)
        flash(u'Perfil actualizado correctamente', 'success')
    return render_template('settings.html', user=current_user, form=form)


@app.route('/solicitudes', methods=['GET'])
@login_required
def get_friend_requests():
    requests = Friendship.get_unconfirmed_from_friend(current_user)
    return render_template(
        'friend_requests.html', user=current_user, requests=requests)


@app.route('/solicitudes/<id>', methods=['POST'])
@login_required
def post_accept_request(id):
    friendship = Friendship.objects(id=id).first()
    if not friendship or not friendship.can_confirm(current_user):
        abort(404)
    friendship.confirm()
    return redirect(url_for('get_friend_requests'))


@app.route('/usuarios/<username>', methods=['GET'])
@login_required
def get_profile(username):
    visited_user = User.objects(username=username).first()
    if not visited_user:
        abort(404)
    friendship = Friendship.get_from_users([current_user, visited_user])
    activities = Activity.objects(creator=visited_user).order_by('-created')
    return render_template(
        'profile.html', user=current_user, visited_user=visited_user,
        activities=activities, friendship=friendship)


@app.route('/usuarios/<username>/solicitud', methods=['POST'])
@login_required
def post_friend_request(username):
    visited_user = User.objects(username=username).first()
    if not visited_user or visited_user == current_user:
        abort(404)
    Friendship.create(creator=current_user, friend=visited_user)
    return redirect(url_for('get_profile', username=visited_user.username))


@app.route('/usuario/amigos/<username>', methods=['POST'])
@login_required
def post_remove_friend(username):
    user = User.objects(username=username).first()
    if not user:
        abort(404)

    friendship = Friendship.get_from_users([current_user, user])
    if not friendship:
        abort(404)

    friendship.delete()

    return redirect(url_for('get_profile', username=user.username))


@app.route('/locales/<localname>', methods=['GET'])
@login_required
def get_local_profile(localname):
    local = Local.get_by_localname(localname)
    if not local:
        abort(404)
    return render_template(
        'local_profile.html', user=current_user, local=local)


@app.route('/locales', methods=['GET'])
@login_required
def get_locals():
    form = LocalForm(localname='', location='')
    return render_template('locals.html', user=current_user, form=form)


@app.route('/locales', methods=['POST'])
@login_required
def post_locals():
    localname = request.form['localname']
    location = request.form['location']
    form = LocalForm(localname=localname, location=location)

    if not form.validate():
        return render_template(
            'locals.html', user=current_user, error=True, form=form)

    Local.create_local(localname, location)
    return redirect(url_for('get_local_profile', localname=localname))


@app.route('/entrar', methods=['GET'])
def get_login():
    form = LoginForm(username='', password='')
    return render_template('login.html', form=form)


@app.route('/entrar', methods=['POST'])
def post_login():
    form = LoginForm(request.form)

    if not form.validate():
        return render_template('login.html', form=form)

    user = User.authenticate(form.username.data, form.password.data)
    if not user:
        return render_template('login.html', error=True, form=form)

    login_user(user)
    return redirect(url_for('get_index'))


@app.route('/registrarse', methods=['GET'])
def get_register():
    form = RegisterForm(
        username='', firstname='', lastname='',
        password='', email='', confirm='')
    return render_template('register.html', form=form)


@app.route('/registrarse', methods=['POST'])
def post_register():
    form = RegisterForm(request.form)

    if not form.validate():
        return render_template('register.html', error=True, form=form)

    user = User.register(form)

    key = utils.generate_key()
    redis.set('activation:key:' + key, user.id)
    # expirar en 24h
    redis.expire('activation:key:' + key, 60*60*24)

    mailer.send_validation_email(user, key)

    login_user(user)
    return redirect(url_for('get_index'))


@app.route('/recuperar-clave', methods=['GET'])
def get_forgot_password():
    return render_template('forgot_password.html')


@app.route('/recuperar-clave', methods=['POST'])
def post_forgot_password():
    username = request.form['username']
    user = User.objects(username=username).first()
    if user:
        key = utils.generate_key()
        redis.set('reset:key:' + key, user.id)
        # expirar en 24h
        redis.expire('reset:key:' + key, 60*60*24)
        mailer.send_reset_password_email(user, key)
    # we say that is correct anyway for not allowing
    # discovery of registered users
    flash(u'Email de recuperacion de contraseña \
        enviado correctamente.', 'success')
    return redirect(url_for('get_login'))


@app.route('/resetear-clave', methods=['GET'])
def get_reset_password():
    key = request.args.get('key')
    userid = redis.get('reset:key:' + key)
    if not userid:
        abort(404)
    return render_template('reset_password.html')


@app.route('/resetear-clave', methods=['POST'])
def post_reset_password():
    key = request.args.get('key')
    password = request.form['password']

    if not password:
        return render_template('reset_password.html')

    username = redis.get('reset:key:' + key)
    if not username:
        abort(404)

    user = User.object(username=username)
    user.update_password(password)
    user.save()
    redis.delete('reset:key:' + key)

    flash(u"Contraseña actualizada correctamente.", 'success')
    return redirect(url_for('get_login'))


@app.route('/salir')
@login_required
def get_logout():
    logout_user()
    return redirect(url_for('get_login'))


@app.route('/activar', methods=['GET'])
def get_activate():
    key = request.args.get('key')

    userid = redis.get('activation:key:' + key)
    if not userid:
        abort(404)

    user = User.objects(id=userid).first()
    user.activate()
    login_user(user)
    redis.delete('activation:key:' + key)
    flash(u"Usuario validado correctamente.", 'success')
    return redirect(url_for('get_index'))


@app.route('/reenviar-confirmacion', methods=['GET'])
@login_required
def get_resend():
    if not current_user.activated:
        key = utils.generate_key()
        redis.set('activation:key:' + key, current_user.id)
        # expirar en 24h
        redis.expire('activation:key:' + key, 60*60*24)

        mailer.send_validation_email(current_user, key)
        flash(u"Email de confirmación reenviado.", 'success')
    else:
        flash(u"Su cuenta ya se encuentra validada.", 'danger')
    return redirect(url_for('get_index'))


# API
###############################################################################


@app.route('/api/search/users', methods=['GET'])
def get_user_search():
    q = request.args.get('q')
    users = User.search(q, 5)
    return users.to_json()


@app.route('/api/search/locals', methods=['GET'])
def get_local_search():
    q = request.args.get('q')
    locals = Local.objects(localname__icontains=q).limit(5)
    return locals.to_json()


# ERROR HANDLERS
###############################################################################


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()