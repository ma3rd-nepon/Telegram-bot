from flask_login import *
from flask_restful import *
from sqlalchemy.orm import *
from flask import *

from data import db_session
from data.users import User
from data.util import get_special_key
from forms.user import RegisterForm, LoginForm, Profile, SetTelegramId
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
    """Get logined user info (get() func becauser filter not work in this mesto)"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# logging.basicConfig(level=logging.INFO, filename="app.log",
#                     format="%(asctime)s %(levelname)s %(name)s %(message)s")


@app.errorhandler(404)
def not_found(error):
    """404 handler alo"""
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    """400 handler"""
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/")
def index():
    """Main site"""
    return render_template("index.html")


@app.route("/profile")
def check_profile():
    """profile site"""
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    if user_id is not None:
        data = db_sess.query(User).filter(User.id == user_id).first().to_dict(rules=('-hashed_password', '-special_api'))
        data["auth"] = True
        data["bio"] = profiles_bio[int(data.get("position"))]
    else:
        data = {
                "name": "Неизвестный", 
                "surname": "Пользователь", 
                "position": "0", 
                "login date": "Неизвестно",
                "auth": False,
                "email": "None",
                "special_api": "У вас нет его",
                "bio": profiles_bio[0],
                "telegram_id": 0
                }
    form = Profile(data)
    return render_template("profile.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    """Register form"""
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
    """Login form"""
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


@app.route("/set_tg_id", methods=["GET", "POST"])
def tgidset():
    """Make relation ship with site account and telegram"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login pls"})

    db_sess = db_session.create_session()

    # if current_user.telegram_id != 0:
    #     return jsonify({"notice": "you already have telegram_id"})

    form = SetTelegramId()
    if form.validate_on_submit():
        try:
            result = "ID изменен" if current_user != 0 else "ID установлен"

            db_sess.query(User).filter(User.id == current_user.id).update(
                {"telegram_id": int(form.telegram_id.data)})
            db_sess.commit()
            raise WindowsError(result)
        except (ValueError, WindowsError) as e:
            name = type(e).__name__
            if name == "ValueError":
                message = "Напишите числовое значение ID, без букв"
            else:
                message = str(e)

            return render_template('set_telegram_id_page.html',
                                   title='Аавывалоыв',
                                   form=form,
                                   message=message)

    return render_template('set_telegram_id_page.html', title='Аавывалоыв', form=form)


@app.route("/users", methods=["GET", "POST", "PUT", "DELETE"])
def users_list():
    """Get users list/definite user"""
    db_sess = db_session.create_session()
    match request.method:
        case "GET":
            type_of_list = request.args.get("type")
            if type_of_list is None:
                return jsonify({"error": "/users?type=<type of users list>"})

            elif type_of_list == "site":
                dictionary = dict()
                user = db_sess.query(User).all()
                for u in user:
                    dictionary[user.index(u)] = u.to_dict(rules=('-hashed_password', '-special_api'))

            elif type_of_list == "bot":
                dictionary = dict()
                user = db_sess.query(BotUser).all()
                for u in user:
                    dictionary[user.index(u)] = u.to_dict(rules=("-skey", '-modify_date'))

            elif type_of_list == "user":
                token = request.args.get("token")
                telegram_id = request.args.get("telegram_id")

                if telegram_id is not None:
                    try:
                        dictionary = db_sess.query(BotUser).filter(BotUser.telegram_id == telegram_id).first().to_dict(rules=("-skey", '-modify_date'))
                    except Exception as e:
                        dictionary = {"error": str(e)}

                elif token is not None:
                    try:
                        dictionary = db_sess.query(User).filter(User.special_api == token).first().to_dict(
                            rules=('-hashed_password', '-special_api'))
                    except Exception as e:
                        dictionary = {"error": str(e)}

                else:
                    dictionary = {"error": "use telegram id or token in params in URL"}
            else:
                dictionary = {"error": "error"}

            return jsonify(dictionary)

        case "POST":
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

        case "PUT":
            token = request.args.get("token")
            telegram_id = request.args.get("telegram_id")
            try:
                js = request.get_json(force=True)
            except:
                return jsonify({"error": "No JSON"})

            try:
                user = db_sess.query(BotUser).filter(BotUser.telegram_id == telegram_id).update(js)
                db_sess.commit()
                return jsonify({"status": "OK"})
            except Exception as e:
                return jsonify({"error": str(e)})

        case "DELETE":
            token = request.args.get("token")
            telegram_id = request.args.get("telegram_id")

            try:
                user = db_sess.query(BotUser).filter(BotUser.telegram_id == telegram_id).first().delete()
                db_sess.commit()
                return jsonify({"status": "OK"})
            except Exception as e:
                return jsonify({"error": f"{e}"})

        case _:
            return jsonify({"error": "error"})


@app.route("/terms_of_use", methods=["GET"])
def terms_pf_use_mysite():
    """terms of use"""
    return render_template("terms_of_use.html")


@app.route('/logout')
@login_required
def logout():
    """logout"""
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/database.db")

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

    app.run()


main()
