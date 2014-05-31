# -*- coding: utf-8 -*-

import re
from wtforms import Form, TextField, PasswordField, validators, TextAreaField
from wtforms import SelectField, RadioField
from flask.ext.login import current_user
from models import User, Local, Tasting

USERNAME_RE = r"^\w+$"

def unique_username(form, field):
    user = User.objects(username=field.data).first()
    if user and (current_user.is_anonymous() or user.id != current_user.id):
        raise validators.ValidationError(
            u'El nombre de usuario ya existe.')

def unique_localname(form, field):
    slug = Local.slugify(field.data)
    local = Local.get_by_slug(slug)
    if local:
        raise validators.ValidationError(
            u'El nombre de local ya existe.')

def unique_tasting_name(form, field):
    slug = Tasting.slugify(field.data)
    tasting = Tasting.get_by_slug(slug)
    if tasting:
        raise validators.ValidationError(
            u'El nombre de degustación ya existe.')

def local_exists(form, field):
    slug = Local.slugify(field.data)
    local = Local.get_by_slug(slug)
    if not local:
        raise validators.ValidationError(
            u'El local no existe o no está registrado en el sistema.')

def strip(s):
    return s.strip()


class RegisterForm(Form):
    username = TextField('username', default='', filters=[strip], validators=[
            validators.Length(
                min=1,
                max=16,
                message=u'El nombre de usuario debe tener entre 1 y 16 caracteres.'
            ),
            validators.Regexp(
                USERNAME_RE,
                message=u"El nombre de usuario contiene caracteres inválidos"
            ),
            validators.Required(message=u'Debes introducir un nombre de usuario.'),
            unique_username
    ])
    firstname = TextField('firstname', default='', filters=[strip], validators=[
        validators.Length(
            min=1, max=16,
            message=u'El nombre debe tener entre 1 y 16 caracteres.'),
        validators.Required(message=u'Debes introducir un nombre.')
    ])
    lastname = TextField('lastname', default='', filters=[strip], validators=[
            validators.Optional(),
            validators.Length(
                max=16,
                message=u'Los apellidos deben tener como máximo 16 caracteres.'
            )
    ])
    email = TextField('email', default='', filters=[strip], validators=[
        validators.Required(message=u'Debes introducir un email.'),
        validators.Email(message=u'Email no válido.')
    ])
    password = PasswordField('password', default='', validators=[
        validators.Required(message=u'Debes introducir una contraseña.'),
        validators.Length(
            min=6,
            max=64,
            message=u'La contraseña debe tener entre 6 y 64 caracteres.'
        ),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    confirm = PasswordField('confirm')


class ProfileForm(RegisterForm):
    password = PasswordField('password', default='', validators=[
        validators.Optional(),
        validators.Length(
            min=6,
            max=64,
            message=u'La contraseña debe tener entre 6 y 64 caracteres.'
        ),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    location = TextField('location', default='', validators=[
        validators.Optional(),
        validators.Length(
            min=6, max=16,
            message=u'La ubicación debe tener entre 6 y 16 caracteres.'),
    ])


class LoginForm(Form):
    username = TextField('username', default='', filters=[strip], validators=[
        validators.Length(
            min=1,
            max=16,
            message=u'El nombre de usuario debe tener entre 1 y 16 caracteres.'
        ),
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
    name = TextField('name', default='', filters=[strip], validators=[
        validators.Length(
            min=1,
            max=16,
            message=u'El nombre del local debe tener entre 1 y 16 caracteres.'
        ),
        validators.Required(message=u'Debes introducir un nombre de local.'),
        unique_localname
    ])
    location = TextField('address', default='', filters=[strip], validators=[
        validators.Required(message=u'Debes introducir una localización.')
    ])
    description = TextAreaField('description', default='', filters=[strip], validators=[
        validators.Optional(),
        validators.Length(
            max=240,
            message=u'La descripción debe ocupar 240 caracteres o menos.')
    ])

class ResetPasswordForm(Form):
    password = PasswordField('password', default='', validators=[
        validators.Required(message=u'Debes introducir una contraseña.'),
        validators.Length(
            min=6,
            max=64,
            message=u'La contraseña debe tener entre 6 y 64 caracteres.'
        ),
        validators.EqualTo('confirm', message=u'Las contraseñas no coinciden.')
    ])
    confirm = PasswordField('confirm')

class TastingForm(Form):
    name = TextField('name', default='', filters=[strip], validators=[
        validators.Length(
            min=1,
            max=40,
            message=u'El nombre del local debe tener entre 1 y 40 caracteres.'
        ),
        validators.Required(message=u'Debes introducir un nombre.'),
        unique_tasting_name
    ])
    local_name = TextField('local_name', default='', filters=[strip], validators=[
        validators.Required(message=u'Debes introducir el local al que pertenece el plato.'),
        local_exists
    ])
    description = TextAreaField('description', default='', filters=[strip], validators=[
        validators.Optional(),
        validators.Length(
            max=240,
            message=u'La descripción debe ocupar 240 caracteres o menos.')
    ])
    taste = SelectField('taste', choices=[
        ('sweet', 'Dulce'),('salty','Salado'), ('bitter', 'Amargo'), ('acid',u'Ácido'), ('spicy','Picante')],
        validators=[
        validators.Optional()
    ])
    origin = SelectField('origin', choices=[("Afghanistan","Afghanistan"),("Albania","Albania"),("Algeria","Algeria"),("American Samoa","American Samoa"),("Andorra","Andorra"),("Angola","Angola"),("Anguilla","Anguilla"),("Antarctica","Antarctica"),("Antigua and Barbuda","Antigua and Barbuda"),("Argentina","Argentina"),("Armenia","Armenia"),("Aruba","Aruba"),("Australia","Australia"),("Austria","Austria"),("Azerbaijan","Azerbaijan"),("Bahamas","Bahamas"),("Bahrain","Bahrain"),("Bangladesh","Bangladesh"),("Barbados","Barbados"),("Belarus","Belarus"),("Belgium","Belgium"),("Belize","Belize"),("Benin","Benin"),("Bermuda","Bermuda"),("Bhutan","Bhutan"),("Bolivia","Bolivia"),("Bosnia and Herzegovina","Bosnia and Herzegovina"),("Botswana","Botswana"),("Bouvet Island","Bouvet Island"),("Brazil","Brazil"),("British Indian Ocean Territory","British Indian Ocean Territory"),("Brunei Darussalam","Brunei Darussalam"),("Bulgaria","Bulgaria"),("Burkina Faso","Burkina Faso"),("Burundi","Burundi"),("Cambodia","Cambodia"),("Cameroon","Cameroon"),("Canada","Canada"),("Cape Verde","Cape Verde"),("Cayman Islands","Cayman Islands"),("Central African Republic","Central African Republic"),("Chad","Chad"),("Chile","Chile"),("China","China"),("Christmas Island","Christmas Island"),("Cocos (Keeling) Islands","Cocos (Keeling) Islands"),("Colombia","Colombia"),("Comoros","Comoros"),("Congo","Congo"),("Congo, The Democratic Republic of The","Congo, The Democratic Republic of The"),("Cook Islands","Cook Islands"),("Costa Rica","Costa Rica"),("Cote D'ivoire","Cote D'ivoire"),("Croatia","Croatia"),("Cuba","Cuba"),("Cyprus","Cyprus"),("Czech Republic","Czech Republic"),("Denmark","Denmark"),("Djibouti","Djibouti"),("Dominica","Dominica"),("Dominican Republic","Dominican Republic"),("Ecuador","Ecuador"),("Egypt","Egypt"),("El Salvador","El Salvador"),("Equatorial Guinea","Equatorial Guinea"),("Eritrea","Eritrea"),("Estonia","Estonia"),("Ethiopia","Ethiopia"),("Falkland Islands (Malvinas)","Falkland Islands (Malvinas)"),("Faroe Islands","Faroe Islands"),("Fiji","Fiji"),("Finland","Finland"),("France","France"),("French Guiana","French Guiana"),("French Polynesia","French Polynesia"),("French Southern Territories","French Southern Territories"),("Gabon","Gabon"),("Gambia","Gambia"),("Georgia","Georgia"),("Germany","Germany"),("Ghana","Ghana"),("Gibraltar","Gibraltar"),("Greece","Greece"),("Greenland","Greenland"),("Grenada","Grenada"),("Guadeloupe","Guadeloupe"),("Guam","Guam"),("Guatemala","Guatemala"),("Guinea","Guinea"),("Guinea-bissau","Guinea-bissau"),("Guyana","Guyana"),("Haiti","Haiti"),("Heard Island and Mcdonald Islands","Heard Island and Mcdonald Islands"),("Holy See (Vatican City State)","Holy See (Vatican City State)"),("Honduras","Honduras"),("Hong Kong","Hong Kong"),("Hungary","Hungary"),("Iceland","Iceland"),("India","India"),("Indonesia","Indonesia"),("Iran, Islamic Republic of","Iran, Islamic Republic of"),("Iraq","Iraq"),("Ireland","Ireland"),("Israel","Israel"),("Italy","Italy"),("Jamaica","Jamaica"),("Japan","Japan"),("Jordan","Jordan"),("Kazakhstan","Kazakhstan"),("Kenya","Kenya"),("Kiribati","Kiribati"),("Korea, Democratic People's Republic of","Korea, Democratic People's Republic of"),("Korea, Republic of","Korea, Republic of"),("Kuwait","Kuwait"),("Kyrgyzstan","Kyrgyzstan"),("Lao People's Democratic Republic","Lao People's Democratic Republic"),("Latvia","Latvia"),("Lebanon","Lebanon"),("Lesotho","Lesotho"),("Liberia","Liberia"),("Libyan Arab Jamahiriya","Libyan Arab Jamahiriya"),("Liechtenstein","Liechtenstein"),("Lithuania","Lithuania"),("Luxembourg","Luxembourg"),("Macao","Macao"),("Macedonia, The Former Yugoslav Republic of","Macedonia, The Former Yugoslav Republic of"),("Madagascar","Madagascar"),("Malawi","Malawi"),("Malaysia","Malaysia"),("Maldives","Maldives"),("Mali","Mali"),("Malta","Malta"),("Marshall Islands","Marshall Islands"),("Martinique","Martinique"),("Mauritania","Mauritania"),("Mauritius","Mauritius"),("Mayotte","Mayotte"),("Mexico","Mexico"),("Micronesia, Federated States of","Micronesia, Federated States of"),("Moldova, Republic of","Moldova, Republic of"),("Monaco","Monaco"),("Mongolia","Mongolia"),("Montserrat","Montserrat"),("Morocco","Morocco"),("Mozambique","Mozambique"),("Myanmar","Myanmar"),("Namibia","Namibia"),("Nauru","Nauru"),("Nepal","Nepal"),("Netherlands","Netherlands"),("Netherlands Antilles","Netherlands Antilles"),("New Caledonia","New Caledonia"),("New Zealand","New Zealand"),("Nicaragua","Nicaragua"),("Niger","Niger"),("Nigeria","Nigeria"),("Niue","Niue"),("Norfolk Island","Norfolk Island"),("Northern Mariana Islands","Northern Mariana Islands"),("Norway","Norway"),("Oman","Oman"),("Pakistan","Pakistan"),("Palau","Palau"),("Palestinian Territory, Occupied","Palestinian Territory, Occupied"),("Panama","Panama"),("Papua New Guinea","Papua New Guinea"),("Paraguay","Paraguay"),("Peru","Peru"),("Philippines","Philippines"),("Pitcairn","Pitcairn"),("Poland","Poland"),("Portugal","Portugal"),("Puerto Rico","Puerto Rico"),("Qatar","Qatar"),("Reunion","Reunion"),("Romania","Romania"),("Russian Federation","Russian Federation"),("Rwanda","Rwanda"),("Saint Helena","Saint Helena"),("Saint Kitts and Nevis","Saint Kitts and Nevis"),("Saint Lucia","Saint Lucia"),("Saint Pierre and Miquelon","Saint Pierre and Miquelon"),("Saint Vincent and The Grenadines","Saint Vincent and The Grenadines"),("Samoa","Samoa"),("San Marino","San Marino"),("Sao Tome and Principe","Sao Tome and Principe"),("Saudi Arabia","Saudi Arabia"),("Senegal","Senegal"),("Serbia and Montenegro","Serbia and Montenegro"),("Seychelles","Seychelles"),("Sierra Leone","Sierra Leone"),("Singapore","Singapore"),("Slovakia","Slovakia"),("Slovenia","Slovenia"),("Solomon Islands","Solomon Islands"),("Somalia","Somalia"),("South Africa","South Africa"),("South Georgia and The South Sandwich Islands","South Georgia and The South Sandwich Islands"),("Spain","Spain"),("Sri Lanka","Sri Lanka"),("Sudan","Sudan"),("Suriname","Suriname"),("Svalbard and Jan Mayen","Svalbard and Jan Mayen"),("Swaziland","Swaziland"),("Sweden","Sweden"),("Switzerland","Switzerland"),("Syrian Arab Republic","Syrian Arab Republic"),("Taiwan, Province of China","Taiwan, Province of China"),("Tajikistan","Tajikistan"),("Tanzania, United Republic of","Tanzania, United Republic of"),("Thailand","Thailand"),("Timor-leste","Timor-leste"),("Togo","Togo"),("Tokelau","Tokelau"),("Tonga","Tonga"),("Trinidad and Tobago","Trinidad and Tobago"),("Tunisia","Tunisia"),("Turkey","Turkey"),("Turkmenistan","Turkmenistan"),("Turks and Caicos Islands","Turks and Caicos Islands"),("Tuvalu","Tuvalu"),("Uganda","Uganda"),("Ukraine","Ukraine"),("United Arab Emirates","United Arab Emirates"),("United Kingdom","United Kingdom"),("United States","United States"),("United States Minor Outlying Islands","United States Minor Outlying Islands"),("Uruguay","Uruguay"),("Uzbekistan","Uzbekistan"),("Vanuatu","Vanuatu"),("Venezuela","Venezuela"),("Viet Nam","Viet Nam"),("Virgin Islands, British","Virgin Islands, British"),("Virgin Islands, U.S.","Virgin Islands, U.S."),("Wallis and Futuna","Wallis and Futuna"),("Western Sahara","Western Sahara"),("Yemen","Yemen"),("Zambia","Zambia"),("Zimbabwe","Zimbabwe")],
        validators=[
        validators.Optional()
    ])