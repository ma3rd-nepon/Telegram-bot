from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, IntegerField
from wtforms.validators import DataRequired

import random


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SetTelegramId(FlaskForm):
    telegram_id = StringField('Ваш ид', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class Profile:
    def __init__(self, js):
        self.is_authorized = js.get("auth")
        self.gradient = random.choice(["gradient-custom", "gradient-custom-4", "gradient-custom-3"])
        self.name = js.get("name")
        self.surname = js.get("surname")
        self.position = js.get("position")
        self.login_date = js.get("modify_date")
        self.email = js.get("email")
        self.special_api = js.get("special_api")
        self.bio = js.get("bio")
        self.tg_id = js.get("telegram_id")