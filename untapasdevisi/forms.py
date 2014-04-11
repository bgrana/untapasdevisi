# -*- coding: utf-8 -*-

from wtforms import Form, TextField, PasswordField, validators
from flask.ext.login import current_user
from models import User, Local


def unique_username(form, field):
    user = User.objects(username=field.data).first()
    if user and user.id != current_user.id:
        raise validators.ValidationError('El nombre de usuario ya existe.')


def unique_localname(form, field):
    local = Local.get_by_localname(field.data)
    if local:
        raise validators.ValidationError(u'El nombre de local ya existe.')


class RegisterForm(Form):
    username = TextField('username', validators=[
        validators.Length(
            min=1, max=16,
            message=u'El nombre de usuario debe tener entre 1 y \
            16 caracteres.'),
        validators.Required(message=u'Debes introducir un nombre de usuario.'),
        unique_username
    ])
    firstname = TextField('firstname', validators=[
        validators.Length(
            min=1, max=16,
            message=u'El nombre debe tener entre 1 y 24 caracteres.'),
        validators.Required(message=u'Debes introducir un nombre.')
    ])
    lastname = TextField('lastname', validators=[
        validators.Optional(),
        validators.Length(
            max=16,
            message=u'Los apellidos deben tener como máximo 24 caracteres.')
    ])
    email = TextField('email', validators=[
        validators.Required(message=u'Debes introducir un email.'),
        validators.Email(message=u'Email no válido.')
    ])
    password = PasswordField('password', [
        validators.Required(message=u'Debes introducir una contraseña.'),
        validators.Length(
            min=6, max=64,
            message=u'La contraseña debe tener entre 6 y 64 caracteres.'),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    confirm = PasswordField('confirm')


class ProfileForm(RegisterForm):
    password = PasswordField('password', [
        validators.Optional(),
        validators.Length(
            min=6, max=64,
            message=u'La contraseña debe tener entre 6 y 64 caracteres.'),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    location = TextField('location', validators=[
        validators.Optional(),
        validators.Length(
            min=6, max=16,
            message=u'La ubicación debe tener entre 6 y 16 caracteres.'),
    ])


class LoginForm(Form):
    username = TextField('username', validators=[
        validators.Length(
            min=1, max=16,
            message=u'El nombre de usuario debe tener entre 6 y \
            16 caracteres.'),
        validators.Required(message=u'Debes introducir un nombre de usuario.'),
    ])
    password = PasswordField('password', [
        validators.Required(message=u'Debes introducir una contraseña.')
    ])

    def validate(self):
        # Regular validate
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.authenticate(self.username.data, self.password.data)
        if not user:
            self.username.errors.append(
                u'Nombre de usuario y/o contraseña inválidos.')
            self.password.errors.append(u'')
            return False
        return True


class LocalForm(Form):
    localname = TextField('localname', validators=[
        validators.Length(
            min=1, max=16,
            message=u'El nombre del local debe tener entre 6 y \
            16 caracteres.'),
        validators.Required(message=u'Debes introducir un nombre de local.'),
        unique_localname
    ])
    location = TextField('location', [
        validators.Required(message=u'Debes introducir una localización.')
    ])