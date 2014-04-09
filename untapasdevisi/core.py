# -*- coding: utf-8 -*-

import os
import utils
import datetime

import redis

from babel.dates import format_date, format_timedelta

from flask import Flask, request, render_template, redirect, url_for, abort, flash
from flask.ext.login import LoginManager, login_user, current_user, login_required, logout_user

from models import User, Friendship, Activity, Local, connect_db
from forms import ProfileForm, RegisterForm, LoginForm

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

connect_db()

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
def date_filter(date):
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
    form = ProfileForm(username=current_user.username, email=current_user.email, location=current_user.location)
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
    return render_template('friend_requests.html', user=current_user, requests=requests)


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
    return render_template('profile.html', user=current_user, visited_user=visited_user,
        activities=activities, friendship=friendship)


@app.route('/usuarios/<username>/solicitud', methods=['POST'])
@login_required
def post_friend_request(username):
    visited_user = User.objects(username=username).first()
    if not visited_user or visited_user == current_user:
        abort(404)
    friendship = Friendship.create(creator=current_user, friend=visited_user)
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


@app.route('/locales', methods=['GET'])
def get_locales():
    return render_template('locales.html',user=current_user)


@app.route('/locales/',methods=['POST'])
def post_locales():
    localname = request.form['localname']
    address = request.form['address']

    if not form.validate():
        return render_template('locales.html', user=current_user, error=True)

    local = Local(localname, address)
    local.save()
    return render_template('perfil_local.html', user=current_user)



@app.route('/entrar', methods=['GET'])
def get_login():
    form = LoginForm(username='',password='')
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
    form = RegisterForm(username='', password='', email='',confirm='')
    return render_template('register.html',form=form)


@app.route('/registrarse', methods=['POST'])
def post_register():
    form = RegisterForm(request.form)

    if not form.validate():
        return render_template('register.html', error=True, form=form)

    user = User.register(form.username.data, form.password.data, form.email.data)

    key = utils.generate_key()
    redis.set('activation:key:'+ key, user.id)
    # expirar en 24h
    redis.expire('activation:key:'+ key, 60*60*24)

    utils.send_validation_email(user, key)

    login_user(user)
    return redirect(url_for('get_index'))


@app.route('/recuperar-clave', methods=['GET'])
def get_forgot_password():
    return render_template('forgot_password.html')


@app.route('/recuperar-clave', methods=['POST'])
def post_forgot_password():
    username = request.form['username']
    user = User.object(username=username).first()
    if user:
        key = utils.generate_key()
        redis.set('reset:key:'+ key, user.id)
        # expirar en 24h
        redis.expire('reset:key:'+ key, 60*60*24)
        utils.sent_reset_password_email(user, key)
        flash(u'Email de recuperacion de contraseña enviado correctamente.', 'success')
        return redirect(url_for('get_login'))
    else:
        return render_template('forgot_password.html')


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
        redis.set('activation:key:'+ key, current_user.id)
        # expirar en 24h
        redis.expire('activation:key:'+ key, 60*60*24)

        utils.send_validation_email(current_user, key)
        flash(u"Email de confirmación reenviado.", 'success')
    else:
        flash(u"Su cuenta ya se encuentra validada.", 'danger')
    return redirect(url_for('get_index'))


# ERROR HANDLERS
###############################################################################

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()