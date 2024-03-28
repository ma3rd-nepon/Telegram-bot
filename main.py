from pyrogram import *
from pyrocon import patch
from other.utils import *

import requests


prefix = "/"
command_prefix = get_from_config("prefix")

api_id = get_from_config("api_id")
app = Client(name=get_from_config("name"), 
             api_id=api_id,
             api_hash=get_from_config("api_hash"),
             bot_token=get_from_config("bot_token"),
             )
quiz = patch(app)


@app.on_message(filters.command("start", prefix))
async def start_function(client, message):
    user_id = message.from_user.id
    user = get_user(user_id)
    try:
        name = user["name"]
    except:
        name = message.from_user.first_name
    await message.reply("Рад вас видеть, {}. Чтобы настроить бота для себя, напишите /setting".format(name))


@app.on_message(filters.command("profile", prefix))
async def start_dialog(client, message):
    user_id = message.from_user.id
    user = get_user(user_id)
    {'name': 'Неизвестный', 'registered': '0', 'skey': 'да', 'status': 'user', 'telegram_id': '1242755674'}
    result = f"""
Имя - {user['name']}
Зарегистрирован на сайте - {user['registered']}
Статус в боте - {user['status']}
Телеграм ID - {user['telegram_id']}
API ключ - {user['skey']}
    """
    await message.reply(result)


@app.on_message(filters.command("setting", prefix))  
async def hzhz(client, message):
    user_id = message.from_user.id
    await message.reply("Итак начнем мою настройку!")
    answer = await question(message, 'Вы зарегистрированы на сайте? (Да/Нет)', quiz)
    if "да" in answer.text.lower():
        edit_user(user_id, {"registered": "да"})
        answer = await question(message, "Отправьте мне свой Секретный API (API находится на сайте в профиле)", quiz)
        his_uid = answer.text
        await message.reply("Подождите пока я найду ваш аккаунт")
        user = get_user_by_uid(answer.text)
        if user != {"error": "Not found"}:
            await message.reply("Нашел ваш аккаунт!")
            answer = await question(message, f"Вы {user['name']}? (Да/Нет)", quiz)
            if 'да' in answer.text:
                await message.reply("Отлично! Теперь свяжем ваши учетные записи.")
                if edit_user(user_id, {"skey": his_uid}):
                    await message.reply("Все получилось! Можете проверить профиль, вызвав команду /profile.")
                    return
                await message.reply("К сожалению возникла ошибка! В скором времени починим.")
                return
            elif "нет" in answer.text.lower():
                await message.reply("Прошу прощения вышла какая то ошибка, обратитесь к разработчику за ее решением")
                return
            else:
                await message.reply("Моя твоя не понимать! Пиши да или нет!")
        else:
            await message.reply("Не нашел такого ключа, похоже что вы ввели его неправильно.")
            return
    elif "нет" in answer.text.lower():
        await message.reply("Жаль. Зарегистрируйтесь на сайте https://qwertedrtvghjn.pythonanywhere.com и пройдите настройку снова")
        return
    else:
        await message.reply("Я не понял вашего ответа, при ответе выберите одно утверждение из скобок после вопроса.")
        return


print("bot started work")
app.run()

