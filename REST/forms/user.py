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


class Profile:
    def __init__(self, js):
        self.is_authorized = js.get("auth")
        self.gradient = random.choice(["gradient-custom", "gradient-custom-4", "gradient-custom-3"])
        self.name = js.get("name")
        self.surname = js.get("surname")
        self.access = js.get("access")
        self.login_date = js.get("date of login")
        self.email = js.get("email")
        self.api = js.get("api")

    def json_export(self):
        data = {
                "name": self.name, 
                "surname": self.surname,
                "email": self.email,
                "access": self.access, 
                "date of login": self.login_date
            }
        return data
