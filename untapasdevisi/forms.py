# -*- coding: utf-8 -*-

from wtforms import Form, TextField, PasswordField, validators
from flask.ext.login import current_user
from models import User


def unique_username(form, field):
    user = User.get_by_username(field.data)
    if user and user != current_user:
        raise validators.ValidationError('El nombre de usuario ya existe.')


class ProfileForm(Form):
    username = TextField('username', validators=[
        validators.Length(min=1, max=16, message=u'El nombre de usuario debe tener entre 6 y 16 caracteres.'),
        validators.Required(message='Debes introducir un nombre de usuario.'),
        unique_username
    ])
    email = TextField('email', validators=[
        validators.Required(message='Debes introducir un email.'),
        validators.Email(message='Email no valido.')
    ])
    location = TextField('location', validators=[
        validators.Optional(),
        validators.Length(min=6, max=16, message=u'La ubicación debe tener entre 6 y 16 caracteres.'),
    ])
    password = PasswordField('password', [
        validators.Optional(),
        validators.Length(min=6, max=64, message=u'La contraseña debe tener entre 6 y 64 caracteres.'),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    confirm = PasswordField('confirm')


class RegisterForm(Form):
    username = TextField('username', validators=[
        validators.Length(min=1, max=16, message=u'El nombre de usuario debe tener entre 6 y 16 caracteres.'),
        validators.Required(message=u'Debes introducir un nombre de usuario.'),
        unique_username
    ])
    email = TextField('email', validators=[
        validators.Required(message=u'Debes introducir un email.'),
        validators.Email(message=u'Email no válido.')
    ])
    password = PasswordField('password', [
        validators.Required(message=u'Debes introducir una contraseña.'),
        validators.Length(min=6, max=64, message=u'La contraseña debe tener entre 6 y 64 caracteres.'),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    confirm = PasswordField('confirm')


class LoginForm(Form):
    username = TextField('username', validators=[
        validators.Length(min=1, max=16, message=u'El nombre de usuario debe tener entre 6 y 16 caracteres.'),
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

        user = User.authenticate(self.username.data,self.password.data)
        if not user:
            self.username.errors.append(u'Nombre de usuario y/o contraseña inválidos.')
            self.password.errors.append(u'')
            return False

        return True