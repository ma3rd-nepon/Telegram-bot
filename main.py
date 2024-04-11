from pyrogram import *
from pyrogram.types import *
from pyrocon import patch
from other.utils import *
from other.info import *

import asyncio
import random

prefix = "/"
command_prefix = get_from_config("prefix")

statuses = {
    1: "user",
    2: "admin",
    4: "creator"
}

likes = dict()
vals = dict()

api_id = get_from_config("api_id")
app = Client(name=get_from_config("name"),
             api_id=api_id,
             api_hash=get_from_config("api_hash"),
             bot_token=get_from_config("bot_token"),
             )
quiz = patch(app)


async def main_settings(message, callback=None, send=True) -> None:
    user_language = message.from_user.language_code
    if user_language is None and callback is not None:
        user_language = callback.from_user.language_code
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("site", user_language), callback_data="site"),
         InlineKeyboardButton(translate("language", user_language), callback_data="language")],
        [InlineKeyboardButton(translate("promote", user_language), callback_data="promote")]
    ])
    params = {
        "chat_id": message.chat.id,
        "text": translate("bot_settings", user_language),
        "reply_markup": markup
    }
    if send:
        func = app.send_message

    else:
        func = app.edit_message_text
        params["message_id"] = message.id

    await func(**params)


async def edit_inline_query_likes_buttons(callback) -> None:
    global likes
    like = 0
    dislike = 0
    for i in likes[callback.inline_message_id]:
        if likes[callback.inline_message_id][i] == "like":
            like += 1
        if likes[callback.inline_message_id][i] == "dislike":
            dislike += 1
    await app.edit_inline_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"👍 {like}", callback_data='like'),
         InlineKeyboardButton(f"👎 {dislike}", callback_data='dislike')]
    ]))


@app.on_message(filters.command("message", command_prefix))
async def ksjdk(_, message) -> None:
    await message.reply(message)


@app.on_message(filters.command("start", prefix))  # старт
async def start_function(_, message) -> None:
    user_id = message.from_user.id
    user_language = "ru"
    user = await get_user(message)
    try:
        name = user["name"]
    except:
        name = message.from_user.first_name
    await message.reply(str(translate("welcome", user_language)).format(name))


@app.on_message(filters.command("profile", prefix))  # показать ваш профиль
async def show_profile(_, message) -> None:
    user_id = message.from_user.id
    user = await get_user(message)
    result = f"""
Имя - {user['name']}
Зарегистрирован на сайте - {user['registered']}
Статус в боте - {user['status']}
Телеграм ID - {user['telegram_id']}
DB Token - {user['skey']}
    """
    await message.reply(result)


@app.on_message(filters.command("commands", prefix))  # список всех команд
async def return_all_comms(_, message) -> None:
    user_language = message.from_user.language_code

    result = f"{ta}shell\n{translate('commands_list', user_language)}\n\n"
    coms = await terminal(f'cat "main.py" | grep "{com_str}"')
    coms_len = len(coms.split("\n")) - 1
    for i in coms.split("\n"):
        if len(i.rstrip()) == 0:
            continue
        if "command_prefix" in i:
            result += command_prefix
        else:
            result += prefix
        result += i.split('"')[1]
        result += " -"
        if "#" in i:
            result += i.split('#')[1]
        else:
            result += f" {translate('no_desc', user_language)}"
        result += "\n"
    result += f"\nВсего {coms_len} команд."
    result += ta
    await message.reply(result)
    return


@app.on_message(filters.command("me", command_prefix))
async def get_me(_, message) -> None:
    user = await get_user(message)
    await message.reply(f"{ta}shell\n{user}{ta}")


@app.on_message(filters.command("terminal", command_prefix))
async def get_terminal_command(_, message) -> None:
    user_language = message.from_user.language_code
    user = await get_user(message)

    if user.get("status") != "creator":
        await message.reply(str(translate("func_n_a", user_language)))
        return
    command = " ".join(message.command[1:])  # message.text.split == message.command
    try:
        await message.reply(terminal(command))
    except Exception as e:
        await message.reply(str(e))


@app.on_message(filters.command("setting", prefix))  # настройка бота через инлайн кнопки
async def new_settings(_, message) -> None:
    await main_settings(message, send=True)


@app.on_message(filters.command("exit", command_prefix))  # выйти в окно
async def on_exit_bot(_, message) -> None:
    user_language = message.from_user.language_code
    user = await get_user(message)

    if user['status'] != "creator":
        await message.reply(translate("wrong_com", user_language))
        return
    exit()


@app.on_message(filters.command("gpt", prefix))  # омг гпт чат
async def chat_gpt_answer(_, message) -> None:
    user_language = message.from_user.language_code

    result = await get_cp_response(" ".join(message.command[1:]))
    if "error - " in result:
        await app.send_message(chat_id=get_from_config("owner"), text=result)
        result = translate("error", user_language)
    await message.reply(result)


@app.on_message(filters.command("image", prefix))  # генерация картинок (медленно)
async def draw_prompt(_, message) -> None:
    prompt = " ".join(message.command[1:])
    if prompt == '':
        return
    result = await draw(prompt, str(message.id))
    await app.send_photo(chat_id=message.chat.id, photo=result)


@app.on_message(filters.command("курс", prefix))  # узнать текущий курс валют
async def get_course(_, message) -> None:
    user_language = message.from_user.language_code
    try:
        if len(message.command) > 1:
            val = message.command[1]
            if val in '. -' or val == '':
                val = "usd"
            if len(message.command) > 2:
                count = int(message.command[2])
            else:
                count = 1
        else:
            val, count = 'usd', 1
        result = course(val.upper(), count)
    except Exception as e:
        result = translate("course_error", user_language)
    await message.reply(result)


@app.on_message(filters.command("ip", prefix))  # пробить по айпи (хацкинг)
async def get_ip_location(_, message) -> None:
    user_language = message.from_user.language_code
    try:
        result = location(message.text[4:])
    except Exception as e:
        result = translate("wrong_com", user_language)
    await message.reply(result)


@app.on_message(filters.command("погода", prefix))
async def get_weather(_, message) -> None:
    try:
        result = weather(message.text[8:])
    except:
        result = "Неправильно написан город либо его несуществует"
    await message.reply(result)


@app.on_callback_query()
async def catch_callbacks(_, callback) -> None:
    user_language = callback.message.from_user.language_code
    try:
        if "PRIVATE" not in str(callback.message.chat.type):
            await app.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                        text=translate("only_in_ls", user_language),
                                        reply_markup=None)
            return
    except:
        pass

    if "to_main" in callback.data:
        await main_settings(callback.message, send=False, callback=callback)

    elif "site" in callback.data:
        await app.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text="Настройки сайта", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Найти свою страницу', callback_data="search_logined_account")],
                [InlineKeyboardButton('Редактировать данные', callback_data="site_userdata")],
                [InlineKeyboardButton("Назад", callback_data="to_main")]
            ]))

    elif "search_logined_account" in callback.data:
        await callback.message.reply('потом')

    elif "promote" in callback.data:
        await callback.message.reply("Ожидайте ответа сервера...")
        result = await promots_add(callback.from_user.id)
        await asyncio.sleep(random.randint(1, 5))
        if result:
            text = "Принято! В ближайшем времени администраторы бота рассмотрят вашу заявку и ответят на нее."
        else:
            text = "Вы уже оставляли заявку"
        await callback.message.reply(text)

    elif "language" in callback.data:
        await app.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text="Язык ставится такой же как в вашем приложении телеграма",
                                    reply_markup=InlineKeyboardMarkup([
                                        [InlineKeyboardButton("Назад", callback_data="to_main")]
                                    ]))

    elif "set_ru_lang" in callback.data or "set_en_lang" in callback.data:
        await callback.message.reply("не")

    elif callback.data == "dislike":
        if likes.get(callback.inline_message_id) is None:
            likes[callback.inline_message_id] = dict()
        if 'dislike' in likes[callback.inline_message_id].get(callback.from_user.id):
            likes[callback.inline_message_id][callback.from_user.id] = "nichego"
            return
        likes[callback.inline_message_id][callback.from_user.id] = 'dislike'

        await edit_inline_query_likes_buttons(callback)

    elif callback.data == "like":
        if likes.get(callback.inline_message_id) is None:
            likes[callback.inline_message_id] = dict()
        if 'like' in likes[callback.inline_message_id].get(callback.from_user.id):
            likes[callback.inline_message_id][callback.from_user.id] = "nichego"
            return
        likes[callback.inline_message_id][callback.from_user.id] = 'like'

        await edit_inline_query_likes_buttons(callback)

    elif callback.data == 'get_user':
        res = await get_user(callback)
        await app.edit_inline_text(callback.inline_message_id, text=f'{ta}shell \n{res} {ta}')

    elif "draw_img" in callback.data:
        result = await draw(str(callback.data)[8:], callback.inline_message_id)
        await app.send_photo(chat_id=get_from_config("owner"), photo=result, has_spoiler=True)
        await app.edit_inline_media(inline_message_id=callback.inline_message_id,
                                    media=InputMediaPhoto(f"{callback.inline_message_id}.jpg", caption="not works yet"))
        await app.edit_inline_reply_markup(inline_message_id=callback.inline_message_id,
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton("👍", callback_data='like'),
                                                InlineKeyboardButton("👎", callback_data='dislike')]]))

    elif "gptchat" in callback.data:
        result = await get_cp_response(callback.data.split(":", maxsplit=1)[1])
        await app.edit_inline_text(inline_message_id=callback.inline_message_id, text=result,
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton("👍", callback_data='like'),
                                        InlineKeyboardButton("👎", callback_data='dislike')]]))

    elif "valute" in callback.data:
        a = vals.get(callback.inline_message_id)
        if a is None:
            a = ["USD", 1]
        else:
            a = a.split(":")
        if isinstance(a[1], int):
            result = course(a[0], int(a[1]))
        else:
            result = translate("error", lang)
        await app.edit_inline_text(inline_message_id=callback.inline_message_id, text=result, reply_markup=None)

    elif callback.data.split(":", maxsplit=1)[0] in mon:
        a = callback.data.split(":", maxsplit=1)
        if isinstance(a[1], int):
            await app.edit_inline_text(inline_message_id=callback.inline_message_id,
                                       text=f"Сумма валюты написанa некорректно", reply_markup=None)
            return
        vals[callback.inline_message_id] = callback.data
        await app.edit_inline_text(inline_message_id=callback.inline_message_id,
                                   text=f"Курс {a[0]}, в размере **{a[1]}**", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{i}", f"{i}:{a[1]}") for i in mon],
                [InlineKeyboardButton(translate("get", user_language), callback_data=f"valute")]]))


@app.on_inline_query()
async def answering(_, inline) -> None:
    try:
        await inline.answer(
            results=[
                InlineQueryResultArticle(
                    title="Like or dislike",
                    description="send to chat",
                    input_message_content=InputTextMessageContent(inline.query),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("👍", callback_data='like'),
                         InlineKeyboardButton("👎", callback_data='dislike')]])
                ),
                InlineQueryResultArticle(
                    title="Link for site",
                    description="чтоб не потерять",
                    input_message_content=InputTextMessageContent("Нажми на кнопку чтоб перейти на сайт"),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Ссылка", url="https://qwertedrtvghjn.pythonanywhere.com/")]])
                ),
                InlineQueryResultArticle(
                    title="Get your info",
                    description="из базы данных",
                    input_message_content=InputTextMessageContent(f"получить информацию об аккаунте из базы данных"),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Получить", callback_data="get_user")]])
                ),
                InlineQueryResultArticle(
                    title="Image Generation",
                    description="ждем фикса от пирограма",
                    input_message_content=InputTextMessageContent(f"Генерация картинки, запрос: **{inline.query}**"),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Получить", callback_data=f"draw_img:{inline.query}")]])
                ),
                InlineQueryResultArticle(
                    title="GPT Answer",
                    description="работает",
                    input_message_content=InputTextMessageContent(
                        f"Генерация ответа от Chat GPT, запрос: **{inline.query}**"),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Получить", callback_data=f"gptchat:{inline.query}")]])
                ),
                InlineQueryResultArticle(
                    title="Курс валют",
                    description="Напишите количество",
                    input_message_content=InputTextMessageContent(f"Курс валюты, в размере **{inline.query}**"),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"{i}", f"{i}:{inline.query}") for i in mon],
                        [InlineKeyboardButton("Получить", callback_data=f"valute")]])
                )
            ],
            cache_time=1
        )
    except Exception as e:
        if "[400 MESSAGE_EMPTY]" in str(e):
            return
        print(str(e))


print("bot started work")
app.run()
