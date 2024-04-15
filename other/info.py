import requests
import socket

mon = {
    "USD": "🇺🇲",
    "EUR": "🇪🇺",
    "RUB": "🇷🇺",
    "UAH": "🇺🇦",
    "BYN": "🥔",
    "KZT": "🇰🇿",
}


def location(ip: str):
    result = requests.get(
        f"http://ip-api.com/json/{socket.gethostbyname(ip)}?fields=query,reverse,countryCode,country,regionName,city,zip,lat,lon,timezone,org,as,asname,isp&lang=ru").json()
    text = f'''
IP: {result["query"]}
Хост: {result["reverse"]}

Страна: {result["countryCode"]}/{result["country"]}
Регион: {result["regionName"]}
Город: {result["city"]}
Индекс: {result["zip"]}

Широта: {result["lat"]}
Долгота: {result["lon"]}
Временная зона: {result["timezone"]}

Организация: {result["org"]}
Провайдер: {result["isp"]}
AS: {result["as"]}
ASNAME: {result["asname"]}'''

    return text


async def get_user_info(app, message, user_id):
    chat_id = message.chat.id
    result = await app.get_chat_member(chat_id=chat_id, user_id=user_id)

    fam = f"{result.user.last_name}"
    if "None" in fam or fam is None:
        fam = " "

    if result.user.is_premium:
        emodzi = "🌟"
    else:
        emodzi = " "

    text = f"""
info
Full name: {result.user.first_name}{fam}{emodzi}
ID: {user_id}
Username: @{result.user.username}
Status: {str(result.user.status)[11:].lower().capitalize()}

Chat ID: {chat_id}
Status in chat: {str(result.status)[17:].lower().capitalize()}
Title: {message.chat.title}
  """
    return text


# async def get_users_message_count(app, message):
#     string = ""
#     users = []
#     lst = app.get_chat_members(chat_id=message.chat.id)
#     async for member in lst:
#         try:
#             check = await app.search_messages_count(chat_id=message.chat.id, from_user=member.user.id)
#             users.append([member.user.first_name, check])
#         except Exception as e:
#             pass
#     string += "Топ бездельников чата\n"
#     new_list = sorted(users, key=lambda x: x[1])[::-1]

#     for i in new_list:
#         string += f"{new_list.index(i) + 1}. {i[0]} - {i[1]}\n"

#     all_msgs = await app.search_messages_count(chat_id=message.chat.id)
#     string += f"\nвсего {all_msgs}"

#     return string


def weather(query):
    weather = requests.get('http://api.openweathermap.org/data/2.5/weather',
                           params={'lang': 'ru', 'units': 'metric', 'APPID': '02048c30539276ca0aaca33944aa39c1',
                                   'q': query}).json()
    text = f'''
Погода в {weather["name"]}:
Температура: {round(weather["main"]["temp"], 2)} °C
Ощущается как: {round(weather["main"]["feels_like"], 2)} °C
Скорость ветра: {weather["wind"]["speed"]} м/с
Влажность: {weather["main"]["humidity"]}%
Состояние: {weather["weather"][0]["description"]}
Давление: {round(float(weather['main']['pressure']) / 1000 * 750.06, 2)} мм рт. ст.
    '''
    return text


def course(query, coff=1):
    string = f"Курс валюты {query}\n"
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{query}").json()
    for i in mon:
        string += f"{round(response['rates'][i] * coff, 4)} {i}{mon[i]}\n"
    if query not in mon:
        string += f"{round(response['rates'][query] * coff, 4)} 🏳️{query}\n"
    return string
