from flask_login import *
from flask_restful import *
from sqlalchemy.orm import *
from flask import *

from data import db_session
from data.users import User
from data.util import get_special_key, dictify_user, dictify_bot
from forms.user import RegisterForm, LoginForm, Profile
from data.bot_users import BotUser

import json
import logging
import sqlalchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '9GqXPkMRCoKILBYmnZtDrE96Pekfc1QevzR5gNeL'

profiles_bio = {
    0: "Неизвестно",
    1: "Стандартный пользователь",
    2: "Администратор проекта",
    4: "Создатель"
}

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# logging.basicConfig(level=logging.INFO, filename="app.log",
#                     format="%(asctime)s %(levelname)s %(name)s %(message)s")


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
        data = dictify_user(db_sess.query(User).filter(User.id == user_id).first())
        data["auth"] = True
        data["bio"] = profiles_bio[int(data.get("position"))]
        form = Profile(data)
    else:
        unknown_user = {
                "name": "Неизвестный", 
                "surname": "Пользователь", 
                "position": "0", 
                "login date": "Неизвестно",
                "auth": False,
                "email": "None",
                "special_api": "У вас нет его",
                "bio": profiles_bio[0]
                }
        form = Profile(unknown_user)
    return render_template("profile.html", form=form)



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
            special_api=get_special_key(form.email.data)
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Вы успешно зарегистрировались")
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


@app.route("/user/add/<uid>", methods=['POST'])
def add_user_to_db(uid):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = dictify_user(db_sess.query(User).filter(User.special_api == uid).first())
        user_uid = user.get('special_api')
        user_pos = user.get("position")
    except:
        return jsonify({"error": "wrong UID"})

    if user_pos < 2:
        return jsonify({"error": f"The required access level - 2, you have the {user_pos} level."})
    else:
        try:
            js = request.get_json(force=True)
        except:
            return jsonify({"error": "No JSON"})

        bot_user = BotUser(
            telegram_id=int(js.get('telegram_id')),
            name=js.get('name'),
            status=js.get('status')
            )
        db_sess.add(bot_user)
        db_sess.commit()
        return jsonify({"status": "OK"})


@app.route("/user/get/<uid>/<tg_id>", methods=['GET', 'POST'])
def get_user_from_db(uid, tg_id):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = dictify_user(db_sess.query(User).filter(User.special_api == uid).first())
        user_uid = user.get("UID")
        user_pos = user.get("position")
    except Exception as e:
        print(e)
        return jsonify({"error": "wrong UID"})
    else:
        try:
            user = dictify_bot(db_sess.query(BotUser).filter(BotUser.telegram_id == tg_id).first())
            return jsonify(user)
        except Exception as e:
            return jsonify({"error": "no users with this ID were found"})


@app.route("/user/get_by_api/<uid>/<target_uid>", methods=['GET', 'POST'])
def get_user_by_api_from_db(uid, target_uid):
    db_sess = db_session.create_session()
    try:
        user = dictify_user(db_sess.query(User).filter(User.special_api == uid).first())
        user_uid = user.get("UID")
        user_pos = user.get("position")
    except:
        return jsonify({"error": "wrong UID"})

    if user_pos < 2:
        return jsonify({"error": f"The required access level - 2, you have the {user_pos} level."})
    else:
        user = dictify_user(db_sess.query(User).filter(User.special_api == target_uid).first())
        return jsonify(user)


@app.route("/user/edit/<uid>/<tg_id>", methods=['GET', 'POST'])
def edit_user_uid(uid, tg_id):
    db_sess = db_session.create_session()
    try:
        user = dictify_user(db_sess.query(User).filter(User.special_api == uid).first())
        user_uid = user.get("UID")
        user_pos = user.get("position")
    except:
        return jsonify({"error": "wrong UID"})

    if user_pos < 2:
        return jsonify({"error": f"The required access level - 2, you have the {user_pos} level."})
    else:
        try:
            js = request.get_json(force=True)
        except:
            return jsonify({"error": "No JSON"})
        try:
            user = db_sess.query(BotUser).filter(BotUser.telegram_id == tg_id).update(js)
            db_sess.commit()
            return jsonify({"status": "OK"})
        except Exception as e:
            return jsonify({"error": str(e)})
        


@app.route("/user/get_all/<uid>/<t>", methods=['GET', 'POST'])
def get_all_users_from_db(uid, t):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = dictify_user(db_sess.query(User).filter(User.special_api == uid).first())
        user_uid = user.get("UID")
        user_pos = user.get("position")
    except:
        return jsonify({"error": "wrong UID"})

    if user_pos < 2:
        return jsonify({"error": f"The required access level - 2, you have the {user_pos} level."})
    else:
        dictionary = dict()
        if t == "site":
            user = db_sess.query(User).all()
            for u in user:
                dictionary[user.index(u)] = dictify_user(u)
            return jsonify(dictionary)

        elif t == "bot":
            user = db_sess.query(BotUser).all()
            for u in user:
                dictionary[user.index(u)] = dictify_bot(u)
            return jsonify(dictionary)
        else:
            return "error"


@app.route("/user/delete/<uid>/<tg_id>", methods=['GET', 'POST'])
def delete_user_from_db(uid, tg_id):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    try:
        user = dictify_user(db_sess.query(User).filter(User.special_api == uid).first())
        user_uid = user.get("UID")
        user_pos = user.get("position")
    except:
        return jsonify({"error": "wrong UID"})

    if user_pos < 4:
        return jsonify({"error": f"The required access level - 3, you have the {user_pos} level."})
    else:
        try:
            user = db_sess.query(BotUser).filter(BotUser.telegram_id == tg_id).first().delete()
            db_sess.commit()
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
    #         position=4,
    #         special_api="17932087:0nIh1WakJiOikGchJye"
    #     )
    # user.set_password("no_iii12345")
    # db_sess.add(user)
    # db_sess.commit()