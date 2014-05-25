# -*- coding: utf-8 -*-

import datetime

import redis

from babel.dates import format_date, format_timedelta

from flask import Flask, request, render_template, redirect, url_for
from flask import abort, flash, send_from_directory
from flask.ext.login import LoginManager, login_user, current_user
from flask.ext.login import login_required, logout_user

import support
from models import User, Friendship, Activity, Local, Like, Vote
from models import LikeActivity, connect_db, DislikeActivity, Tasting
from forms import ProfileForm, RegisterForm, LoginForm, LocalForm
from forms import ResetPasswordForm, TastingForm
from werkzeug import secure_filename
import os

# Setup
###############################################################################

app = Flask(__name__)
IMG_PATH = 'images'
UPLOAD_FOLDER = os.path.join(app.root_path, IMG_PATH)
app.config.from_object(__name__)
app.config.update({
    'DEBUG': True,
    'SECRET_KEY': 'development_key',
    'HOST': '127.0.0.1:5000',
    'MAILGUN_API_USER': 'sandbox74944',
    'MAILGUN_API_KEY': 'key-84mxu54004c5y47zgym0z-d34jnsvl18',
    'MONGODB_DB_NAME': 'untapasdevisi',
    'REDIS_URL': 'localhost',
    'UPLOAD_FOLDER': UPLOAD_FOLDER,
    'ALLOWED_EXTENSIONS': set(['jpg', 'png'])
})

postman = support.Postman(
    app.config['MAILGUN_API_USER'],
    app.config['MAILGUN_API_KEY'],
    app.config['HOST']
)

redis = redis.from_url(app.config['REDIS_URL'])

vault = support.Valut(redis)

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
    user = User.objects(username=current_user.username).first()
    activities = Activity.search(current_user.id, user).order_by('-created').limit(10)
    return render_template('index.html', user=current_user,
        friends=friends, activities=activities)


@app.route('/configuracion', methods=['GET'])
@login_required
def get_settings():
    form = ProfileForm(
        username=current_user.username,
        email=current_user.email,
        firstname=current_user.firstname,
        lastname=current_user.lastname,
        location=current_user.location
    )
    image = current_user.avatar
    return render_template('settings.html', user=current_user, form=form, image=image)


@app.route('/configuracion', methods=['POST'])
@login_required
def post_settings():
    form = ProfileForm(request.form)
    if form.validate():
        current_user.update(form)
        flash(u'Perfil actualizado correctamente', 'success')
    return redirect(url_for('get_settings'))


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['image']
    if not file:
        flash(u'No has seleccionado ninguna imagen','warning')
        return redirect(url_for('get_settings'))
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    user = User.objects(username=current_user.username).first()
    user.avatar = url_for('uploaded_file', filename=filename)
    user.save()
    flash(u'Foto de perfil actualizada', 'success')
    form = ProfileForm(
        username=current_user.username,
        email=current_user.email,
        firstname=current_user.firstname,
        lastname=current_user.lastname,
        location=current_user.location
    )
    return redirect(url_for('get_settings'))


@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/solicitudes', methods=['GET'])
@login_required
def get_friend_requests():
    requests = Friendship.get_unconfirmed_from_friend(current_user)
    return render_template('friend_requests.html',
        user=current_user, requests=requests)


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
    image = visited_user.avatar
    friendship = Friendship.get_from_users([current_user, visited_user])
    activities = Activity.objects(creator=visited_user).order_by('-created').limit(10)
    return render_template(
        'profile.html', user=current_user, visited_user=visited_user,
        activities=activities, friendship=friendship, image=image)


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


@app.route('/locales', methods=['GET'])
@login_required
def get_locals():
    form = LocalForm(name='', adrress='')
    return render_template('locals.html', user=current_user, form=form)


@app.route('/locales', methods=['POST'])
@login_required
def post_locals():
    form = LocalForm(request.form)

    if not form.validate():
        return render_template(
            'locals.html', user=current_user, error=True, form=form)

    file = request.files['image']
    if not file:
        local = Local.create_local(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data
        )
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        local = Local.create_local(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data,
            avatar=url_for('uploaded_file', filename=filename)
        )
    return redirect(url_for('get_local_profile', slug=local.slug))


@app.route('/locales/<slug>', methods=['GET'])
@login_required
def get_local_profile(slug):
    local = Local.get_by_slug(slug)
    if not local:
        abort(404)
    like = Like.get_by_local_and_user(local, current_user)
    activities = Activity.objects(target=local).order_by('-created').limit(10)
    return render_template('local_profile.html',
        user=current_user, local=local, like=like, activities=activities)


@app.route('/locales/<slug>/megusta', methods=['POST'])
@login_required
def post_local_like(slug):
    local = Local.get_by_slug(slug)
    if not local:
        abort(404)

    user = User.objects(username=current_user.username).first()
    like = Like.create(local, user)
    return redirect(url_for('get_local_profile', slug=local.slug))


@app.route('/locales/<slug>/nomegusta', methods=['POST'])
@login_required
def post_local_dislike(slug):
    local = Local.get_by_slug(slug)
    if not local:
        abort(404)

    like = Like.get_by_local_and_user(local, current_user)
    if not like:
        abort(404)

    user = User.objects(username=current_user.username).first()
    DislikeActivity.create(local, user)
    like.delete()
    return redirect(url_for('get_local_profile', slug=local.slug))


@app.route('/degustaciones/<slug>', methods=['GET'])
@login_required
def get_tasting_profile(slug):
    tasting = Tasting.get_by_slug(slug)
    if not tasting:
        abort(404)

    activities = Activity.objects(target=tasting).order_by('-created').limit(10)
    vote = Vote.objects(user=current_user.id, tasting=tasting.id).first()
    if vote:
        return render_template('tasting_profile.html',
            user=current_user, tasting=tasting,
            activities=activities, vote=vote)
    else:
        return render_template('tasting_profile.html',
            user=current_user, tasting=tasting,
            activities=activities, vote=None)


@app.route('/degustaciones', methods=['GET'])
@login_required
def get_tastings():
    form = TastingForm()
    return render_template('tastings.html', form=form, user=current_user)


@app.route('/degustaciones', methods=['POST'])
@login_required
def post_tastings():
    form = TastingForm(request.form)

    if not form.validate():
        return render_template(
            'tastings.html', user=current_user, error=True, form=form)

    file = request.files['image']
    if not file:
        tasting = Tasting.create_tasting(
        name=form.name.data,
        local_name=form.local_name.data,
        recipe=form.recipe.data
        )
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        tasting = Tasting.create_tasting(
            name=form.name.data,
            local_name=form.local_name.data,
            recipe=form.recipe.data,
            avatar=url_for('uploaded_file', filename=filename)
        )
    return redirect(url_for('get_tasting_profile', slug=tasting.slug))


@app.route('/degustaciones/<tasting_slug>/votar', methods=['POST'])
@login_required
def post_vote(tasting_slug):
    user = User.objects(username=current_user.username).first()
    tasting = Tasting.get_by_slug(tasting_slug)
    points = request.form['points']
    vote = Vote.objects(user=user.id, tasting=tasting.id).first()
    if vote:
        vote.update_vote(points)
    else:
        vote = Vote.create_vote(user, tasting, points)
    return redirect(url_for(
        'get_tasting_profile', slug=tasting.slug))

# USERS
################################################################################

@app.route('/entrar', methods=['GET'])
def get_login():
    form = LoginForm()
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
    form = RegisterForm()
    return render_template('register.html', form=form)


@app.route('/registrarse', methods=['POST'])
def post_register():
    form = RegisterForm(request.form)

    if not form.validate():
        return render_template('register.html', error=True, form=form)

    user = User.register(form)
    key = vault.put(user.id, 60*60*24)
    postman.send_validation_email(user, key)

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
        key = vault.put(user.id, 60*60*24)
        postman.send_reset_password_email(user, key)
    # we say that is correct anyway for not allowing
    # discovery of registered users
    msg = u'Email de recuperacion de contraseña enviado correctamente.'
    flash(msg, 'success')
    return redirect(url_for('get_login'))


@app.route('/resetear-clave', methods=['GET'])
def get_reset_password():
    key = request.args.get('key')
    userid = vault.get(key)
    if not userid:
        abort(404)
    form = ResetPasswordForm()
    return render_template('reset_password.html', form=form)


@app.route('/resetear-clave', methods=['POST'])
def post_reset_password():
    key = request.args.get('key')

    userid = vault.get(key)
    if not userid:
        abort(404)

    form = ResetPasswordForm(request.form)

    if not form.validate():
        return render_template('reset_password.html', form=form)

    user = User.objects(id=userid).first()
    user.update_password(form.password.data)
    user.save()
    vault.delete(key)

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

    userid = vault.get(key)
    if not userid:
        abort(404)

    user = User.objects(id=userid).first()
    user.activate()
    login_user(user)
    vault.delete(key)
    flash(u"Usuario validado correctamente.", 'success')
    return redirect(url_for('get_index'))


@app.route('/reenviar-confirmacion', methods=['GET'])
@login_required
def get_resend():
    if not current_user.activated:
        key = vault.put(current_user.id, 60*60*24)
        postman.send_validation_email(current_user, key)
        flash(u"Email de confirmación reenviado.", 'success')
    else:
        flash(u"Su cuenta ya se encuentra validada.", 'danger')
    return redirect(url_for('get_index'))

# SEARCH
################################################################################

@app.route('/buscar', methods=['GET'])
@login_required
def get_search():
    q = request.args.get('q')
    if q == None:
        return render_template('search.html', user=current_user)

    typ = request.args.get('type', 'Users').capitalize()
    if not typ in ['User', 'Local']:
        typ = 'Local'

    if typ == 'User':
        results = User.search(q, 10)

    if typ == 'Local':
        results = Local.search(q, 10)

    return render_template('results.html', q=q, typ=typ,
        user=current_user, results=results)


# API
###############################################################################


@app.route('/api/search/users', methods=['GET'])
def postman_search():
    q = request.args.get('q')
    users = User.search(q, 5)
    return users.to_json()


@app.route('/api/search/locals', methods=['GET'])
def get_local_search():
    q = request.args.get('q')
    locals = Local.search(q, 5)
    return locals.to_json()


# ERROR HANDLERS
###############################################################################


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
