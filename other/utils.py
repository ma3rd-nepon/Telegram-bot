from dotenv import dotenv_values

import requests


config = dotenv_values(".env")


def get_from_config(query):
    """Get variable from .env config"""
    try:
        result = config[query]
    except:
        result = "not found"
    return result


url = "https://qwertedrtvghjn.pythonanywhere.com/post"
api = get_from_config("api")


def get_user(user_id):
    """Get user from database"""
    response = requests.get(f"{url}/user/get/{api}/{user_id}")
    print(response.json())
    if response.json().get("error") == None:
        user = response.json()
    else:
        data = {
            "telegram_id": user_id,
            "name": "Неизвестный",
            "registered": 0
        }
        resp = requests.post(f"{url}/user/add/{api}", json=data)
        get_user(user_id)
    
    return user


def get_all_users(type_of_users):
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
    answer = await quiz.ask(message, text)
    return answer


def edit_user(user_id, data):
    response = requests.post(f"{url}/user/edit/{api}/{user_id}", json=data)
    if response.json() == {"status": "OK"}:
        return True
    return False
