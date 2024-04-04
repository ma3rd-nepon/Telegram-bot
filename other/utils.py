from dotenv import dotenv_values
from freeGPT import AsyncClient
from io import BytesIO
from PIL import Image

import requests
import subprocess

config = dotenv_values(".env")

def get_from_config(query):
    """Get variable from .env config"""
    try:
        result = config[query]
    except:
        result = "not found"
    return result


url = "https://qwertedrtvghjn.pythonanywhere.com"
api = get_from_config("api")
ta = "```"
com_str = "@app.on_message(filters.command("


def get_user(message):
    """Get user from database"""
    user_id = message.from_user.id
    response = requests.get(f"{url}/user/get/{api}/{user_id}")
    if response.json().get("error") == None:
        user = response.json()
    else:
        data = {
            "telegram_id": user_id,
            "name": message.from_user.first_name,
            "registered": 0
        }
        resp = requests.post(f"{url}/user/add/{api}", json=data)
        user = data
    
    return user


def get_userinfo(user_id):
    """Get user info bu tg id"""
    response = requests.get(f"{url}/user/get/{api}/{user_id}")
    if response.json().get("error") == None:
        user = response.json()
        return user
    else:
        data = {
            "telegram_id": user_id,
            "name": message.from_user.first_name,
            "registered": 0
        }
        resp = requests.post(f"{url}/user/add/{api}", json=data)

        return "Вас нет в базе данных"


def get_all_users(type_of_users):
    """Get all users from db (site or bot)"""
    response = requests.get(f"{url}/user/get_all/{api}/{type_of_users}")
    if response.ok:
        return response.json()
    return {"error": "Not found"}


def get_user_by_uid(UID):
    """Get user site account by his uid"""
    response = requests.get(f"{url}/user/get_by_api/{api}/{UID}")
    if response.ok:
        return response.json()
    return {"error": "Not found"}


async def question(message, text, quiz):
    """Quiz question from old settings"""
    answer = await quiz.ask(message, text)
    return answer


def edit_user(user_id, data):
    """Edit user"""
    response = requests.post(f"{url}/user/edit/{api}/{user_id}", json=data)
    if response.json() == {"status": "OK"}:
        return True
    return False


def terminal(command):
    """Terminal"""
    return str(subprocess.check_output(str(command), shell=True).decode("utf-8"))


def promots_add(user_id):
    """Add your promotion to queue"""
    with open('other/promots.txt', 'r') as file:
        f = ",".join(file.readlines())
        if str(user_id) in f:
            return False

    with open('other/promots.txt', 'a') as file:
        file.write(f'\n{user_id}')
        return True


async def get_cp_response(query):
    """omg chat gpt"""
    if query == '':
        query = 'привет'
    text = str(query.encode().decode("utf-8", "ignore"))
    try:
        response = await AsyncClient.create_completion("gpt3", text)
        return response
    except Exception as e:
        return str("error - " + str(e))


async def draw(query, name):
    prompt = query.encode().decode("utf-8", "ignore")
    resp = await AsyncClient.create_generation("prodia", prompt)
    Image.open(BytesIO(resp)).save(f"{name}.jpg")
    return BytesIO(resp)
