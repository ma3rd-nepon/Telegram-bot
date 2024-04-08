from dotenv import dotenv_values
from freeGPT import AsyncClient
from io import BytesIO
from PIL import Image
from .async_requests import Responser

import subprocess

config = dotenv_values(".env")
requests = Responser()


def get_from_config(query):
    """Get variable from .env config"""
    try:
        result = config[query]
    except:
        result = "not found"
    return result


url = get_from_config("rest_url")
api = get_from_config("api")
ta = "```"
com_str = "@app.on_message(filters.command("


async def add_user(js):
    resp = await requests.post(f"{url}/users", json=js)
    return resp.json()


async def get_user(message):
    """Get user from database"""
    user_id = message.from_user.id
    response = await requests.get(f"{url}/users", params={"type": "user", "telegram_id": f"{user_id}"})
    if response.json().get("error") is None:
        user = response.json()
    else:
        data = {
            "telegram_id": user_id,
            "name": message.from_user.first_name,
        }
        resp = await add_user(data)
        print(resp)
        user = data

    return user


async def get_all_users(type_of_users):
    """Get all users from db (site or bot)"""
    response = await requests.get(f"{url}/users", params={"type": f"{type_of_users}"})
    if response.status == 200:
        return response.json()
    return {"error": "Not found"}


async def get_user_by_token(token):
    """Get user site account by his token"""
    response = await requests.get(f"{url}/users", params={"type": "user", "token": f"{token}"})
    if response.status == 200:
        return response.json()
    return {"error": "Not found"}


async def edit_user(data):
    """Edit user"""
    response = await requests.put(f"{url}/users", json=data)
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
