from flask_login import *
from flask_restful import *
from sqlalchemy.orm import *
from flask import *

from data import db_session
from data.users import User
from data.util import get_special_key
from forms.user import RegisterForm, LoginForm, Profile
from data.bot_users import BotUser

import json
import logging
import sqlalchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '9GqXPkMRCoKILBYmnZtDrE96Pekfc1QevzR5gNeL'
api = "BgZlwxZ4VfkOmx270PaPYTiPv6SftVDjvvd80IIN"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

logging.basicConfig(level=logging.INFO, filename="app.log",
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile")
def check_profile():
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    if user_id is not None:
        ad = db_sess.query(User).get(user_id)
        al = str(ad).split(";")
        print()
        print(al, len(al))
        data = {
            "name": al[0], 
            "surname": al[1], 
            "access": al[2], 
            "date of login": al[3], 
            "auth": True, 
            "email": al[4],
            "api": al[5]
            }
        form = Profile(data)
    else:
        unknown_user = {
                "name": "Неизвестный", 
                "surname": "Пользователь", 
                "access": "0", 
                "date of login": "Неизвестно", 
                "auth": False, 
                "email": "None",
                "api": "У вас нет его"
                }
        form = Profile(unknown_user)
    return render_template("profile.html", form=form)


@app.route('/post', methods=['GET', 'POST'])
@login_required
def basic():
    # logging.info('Request: %r', request.json)
    if request.is_json:
        print(request.get_json(force=True))
    if request.method == 'GET':
        response = {"error": "use this with POST method"}
        return jsonify(response)



@app.route('/register', methods=['GET', 'POST'])
def reqister():
    try:
        if current_user.is_authenticated:
            return jsonify({"notice": "you already logined"})
    except:
        pass
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            position=f'default-{form.name.data}',
            special_api=get_special_key(form.name.data)
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return jsonify({"notice": "you already logined"})
    except:
        pass
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return render_template('login.html',
                message="Вы успешно авторизировались. Можете пользоваться сайтом",
                form=form)
        else:
            return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)    
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/post/user/add/<uid>", methods=['POST'])
@login_required
def add_user_to_db(uid):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = str(db_sess.query(User).filter(User.special_api == uid).first()).split(";")
        user_uid = user[5]
        user_pos = user[2]
    except:
        return jsonify({"error": "wrong UID"})

    if "admin" not in user_pos and "creator" not in user_pos:
        return jsonify({"error": "you dont have the rights to perform this action"})
    else:
        try:
            js = request.get_json(force=True)
        except:
            return jsonify({"error": "No JSON"})

        bot_user = BotUser(
            telegram_id=int(js.get('telegram_id')),
            name=js.get('name'),
            status_in_bot=js.get('status')
            )
        db_sess.add(bot_user)
        db_sess.commit()
        return jsonify({"status": "OK"})


@app.route("/post/user/get/<uid>/<tg_id>", methods=['GET', 'POST'])
@login_required
def get_user_from_db(uid, tg_id):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = str(db_sess.query(User).filter(User.special_api == uid).first()).split(";")
        user_uid = user[5]
        user_pos = user[2]
    except:
        return jsonify({"error": "wrong UID"})

    if "admin" not in user_pos and "creator" not in user_pos:
        return jsonify({"error": "you dont have the rights to perform this action"})
    else:
        user = str(db_sess.query(BotUser).filter(BotUser.telegram_id == tg_id).first()).split(";")
        return jsonify({
            "name": user[1],
            "telegram_id": user[0], 
            "status in bot": user[2]
            })

@app.route("/post/user/get_all/<uid>/<t>", methods=['GET', 'POST'])
@login_required
def get_all_users_from_db(uid, t):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = str(db_sess.query(User).filter(User.special_api == uid).first()).split(";")
        user_uid = user[5]
        user_pos = user[2]
    except:
        return jsonify({"error": "wrong UID"})

    if "admin" not in user_pos and "creator" not in user_pos:
        return jsonify({"error": "you dont have the rights to perform this action"})
    else:
        dictionary = dict()
        if t == "site":
            user = db_sess.query(User).all()
            for u in user:
                us = str(u).split(";")
                dictionary[user.index(u)] = {
                    "name": us[0], 
                    "surname": us[1],
                    "position": us[2],
                    "email": us[4],
                    "UID": us[5]
                    }
            return jsonify(dictionary)

        elif t == "bot":
            user = db_sess.query(BotUser).all()
            for u in user:
                us = str(u).split(";")
                dictionary[user.index(u)] = {
                    "name": us[1],
                    "status": us[2],
                    "telegram_id": us[0]
                    }
            return jsonify(dictionary)
        else:
            return "error"


@app.route("/post/user/delete/<uid>/<tg_id>", methods=['GET', 'POST'])
@login_required
def delete_user_from_db(uid, tg_id):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = str(db_sess.query(User).filter(User.special_api == uid).first()).split(";")
        user_uid = user[5]
        user_pos = user[2]
    except:
        return jsonify({"error": "wrong UID"})

    if "admin" not in user_pos and "creator" not in user_pos:
        return jsonify({"error": "you dont have the rights to perform this action"})
    else:
        try:
            user = db_sess.query(BotUser).filter(BotUser.telegram_id == tg_id).first().delete()
            return jsonify({"status": "OK"})
        except Exception as e:
            return jsonify({"error": f"{e}"})
            

@app.route("/terms_of_use", methods=["GET"])
def terms_pf_use_mysite():
    return render_template("terms_of_use.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("mysite/db/database.db")

    db_sess = db_session.create_session()
    db_sess.commit()

    # user = User(
    #         email="example@ex.com",
    #         name="dima",
    #         surname="indus",
    #         position=f'admin-dima',
    #         special_api=get_special_key("dima")
    #     )
    # user.set_password("no_iii12345")
    # db_sess.add(user)
    # db_sess.commit()
