from dotenv import dotenv_values
from freeGPT import AsyncClient
from io import BytesIO
from PIL import Image
from yamager import Yamager
from help.async_requests import Responser

import subprocess
import asyncio
import json
import random
import os

config = dotenv_values(".env")
requests = Responser()

with open("help/language.json", "r") as file:
    lang = json.load(file)


def translate(word, language) -> str:
    """Get word translated version (from json)"""
    try:
        if language not in ["ru", "en"]:
            language = "en"
        result = lang[word][language].encode("cp1251").decode("utf-8")
    except KeyError as e:
        result = "Translate error"
    return result


def get_from_config(query) -> str:
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
command_prefix = get_from_config("prefix")
prefix = "/"


async def add_user(js) -> dict:
    """Add user to cloud DB"""
    resp = await requests.post(f"{url}/users", json=js)
    return resp.json()


async def get_user(message) -> dict:
    """Get user from DB"""
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
        await asyncio.sleep(2)
        user = await get_user(message)

    return user


async def get_all_users(type_of_users) -> dict:
    """Get all users from db (site or bot)"""
    response = await requests.get(f"{url}/users", params={"type": f"{type_of_users}"})
    if response.status == 200:
        return response.json()
    return {"error": "Not found"}


async def get_user_by_token(token) -> dict:
    """Get user site account by his token"""
    response = await requests.get(f"{url}/users", params={"type": "user", "token": f"{token}"})
    if response.status == 200:
        return response.json()
    return {"error": "Not found"}


async def edit_user(data) -> bool:
    """Edit user, True if success"""
    response = await requests.put(f"{url}/users", json=data)
    if response.json() == {"status": "OK"}:
        return True
    return False


async def terminal(command) -> str:
    """Terminal commands (i want linux)"""
    return str(subprocess.check_output(str(command), shell=True).decode("utf-8"))


async def promots_add(user_id) -> bool:
    """Add your promotion to queue, True if success"""
    with open('help/promots.txt', 'r') as file:
        f = ",".join(file.readlines())
        if str(user_id) in f:
            return False

    with open('help/promots.txt', 'a') as file:
        file.write(f'\n{user_id}')
        return True


async def get_cp_response(query) -> str:
    """omg chat gpt"""
    if query == '':
        query = 'привет'
    text = str(query.encode().decode("utf-8", "ignore"))
    try:
        response = await AsyncClient.create_completion("gpt3", text)
        return response
    except Exception as e:
        return str("error - " + str(e))


async def draw(query, name) -> BytesIO:
    """Draws image (AI) Saving in work directory and returns as BytesIO"""
    prompt = query.encode().decode("utf-8", "ignore")
    resp = await AsyncClient.create_generation("prodia", prompt)
    Image.open(BytesIO(resp)).save(f"{name}.jpg")
    return BytesIO(resp)


async def search_photo(query):
    try:
        yan = Yamager()
        images = yan.search_google_images(str(query))
        # prprprpr
        return random.choice(images)
    except Exception as e:
        return str(e)


def evaluate(primer):
    try:
        return float(eval(primer))
    except (SyntaxError, ZeroDivisionError):
        return ""
    except TypeError:
        return float(eval(primer.replace('(', '*(')))
    except Exception as e:
        print(e)
        return ""


async def commands_list(type_of_commands, user_language):
    if not os.name == "nt":
        comm = "Get-Content"
        comm2 = "Select-String"
    else:
        comm = "cat"
        comm2 = "grep"
    all_commands = ""
    default_commands = ""
    admin_commands = ""

    coms = await terminal(f'{comm} "main.py" | {comm2} "{com_str}"')
    coms_len = len(coms.split("\n")) - 1
    for i in coms.split("\n"):
        res = ''
        if len(i.rstrip()) == 0:
            continue
        if "command_prefix" in i:
            res += command_prefix
        else:
            res += prefix
        res += i.split('"')[1]
        res += " -"
        if "#" in i:
            res += i.split('#')[1]
        else:
            res += f" {translate('no_desc', user_language)}"
        res += "\n"
        if command_prefix in res:
            admin_commands += res
        else:
            default_commands += res
        all_commands += res

    if type_of_commands == "admin_commands":
        target = admin_commands.split('\n')
        admin_commands += f"\nВсего {len(target) - 1} команд."
        total_answer = admin_commands

    elif type_of_commands == "all_commands":
        target = all_commands.split('\n')
        all_commands += f"\nВсего {len(target) - 1} команд."
        total_answer = all_commands

    else:
        target = default_commands.split('\n')
        default_commands += f"\nВсего {len(target) - 1} команд."
        total_answer = default_commands

    return total_answer
