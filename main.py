import os

from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import MessageTooLong, MessageEmpty
from help.utils import *
from help.other.info import *
from help.code_compile import c_compile
from math import sqrt
import asyncio
import random
import re

prefix = "/"
command_prefix = get_from_config("prefix")

statuses = {
    1: "user",
    2: "admin",
    4: "creator"
}

likes = dict()
vals = dict()
inline_calc_text = dict()

api_id = get_from_config("api_id")
app = Client(name=get_from_config("name"),
             api_id=api_id,
             api_hash=get_from_config("api_hash"),
             bot_token=get_from_config("bot_token"),
             )


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


async def image_menu(message, callback=None, send=True) -> None:
    user_language = message.from_user.language_code
    query = str(" ".join(message.text.split(" ")[1:]))
    if user_language is None and callback is not None:
        user_language = callback.from_user.language_code
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("ImageAI", user_language), callback_data=f"image_draw:{query}"),
         InlineKeyboardButton(translate("ImageSearch", user_language), callback_data=f"image_search:{query}")],
        [InlineKeyboardButton(translate("exit", user_language), callback_data="exit")]
    ])

    params = {
        "chat_id": message.chat.id,
        "text": query,
        "reply_markup": markup
    }

    if send:
        func = app.send_message

    else:
        func = app.edit_message_text
        params["message_id"] = message.id

    await func(**params)


def calc_btn(uid, toc="callback_") -> InlineKeyboardMarkup:
    """Calculator buttons, toc - type of callback"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("(", callback_data=f"{toc}calc;{uid};("),
                InlineKeyboardButton(")", callback_data=f"{toc}calc;{uid};)"),
                InlineKeyboardButton("CE", callback_data=f"{toc}calc;{uid};DEL"),
                InlineKeyboardButton("C", callback_data=f"{toc}calc;{uid};C"),
            ],
            [
                InlineKeyboardButton("1/x", callback_data=f"{toc}calc;{uid};**-1"),
                InlineKeyboardButton("^2", callback_data=f"{toc}calc;{uid};**2"),
                InlineKeyboardButton("√", callback_data=f"{toc}calc;{uid};sqrt"),
                InlineKeyboardButton("÷", callback_data=f"{toc}calc;{uid};/"),
            ],
            [
                InlineKeyboardButton("7", callback_data=f"{toc}calc;{uid};7"),
                InlineKeyboardButton("8", callback_data=f"{toc}calc;{uid};8"),
                InlineKeyboardButton("9", callback_data=f"{toc}calc;{uid};9"),
                InlineKeyboardButton("×", callback_data=f"{toc}calc;{uid};*"),
            ],
            [
                InlineKeyboardButton("4", callback_data=f"{toc}calc;{uid};4"),
                InlineKeyboardButton("5", callback_data=f"{toc}calc;{uid};5"),
                InlineKeyboardButton("6", callback_data=f"{toc}calc;{uid};6"),
                InlineKeyboardButton("-", callback_data=f"{toc}calc;{uid};-"),
            ],
            [
                InlineKeyboardButton("1", callback_data=f"{toc}calc;{uid};1"),
                InlineKeyboardButton("2", callback_data=f"{toc}calc;{uid};2"),
                InlineKeyboardButton("3", callback_data=f"{toc}calc;{uid};3"),
                InlineKeyboardButton("+", callback_data=f"{toc}calc;{uid};+"),
            ],
            [
                InlineKeyboardButton("%", callback_data=f"{toc}calc;{uid};*0.01"),
                InlineKeyboardButton("0", callback_data=f"{toc}calc;{uid};0"),
                InlineKeyboardButton(".", callback_data=f"{toc}calc;{uid};."),
                InlineKeyboardButton("=", callback_data=f"{toc}calc;{uid};="),
            ],
        ]
    )


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


@app.on_message(filters.command("message", command_prefix))  # джсон сообщения
@app.on_edited_message(filters.command("message", command_prefix))
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
@app.on_edited_message(filters.command("profile", prefix))
async def show_profile(_, message) -> None:
    user_id = message.from_user.id
    user = await get_user(message)
    result = f"""
Имя - {user.get("bot").get('name')}
Зарегистрирован на сайте - {user.get("bot").get('registered')}
Статус в боте - {user.get('bot').get('status')}
Телеграм ID - {user.get('bot').get('telegram_id')}
    """
    {'bot': {'id': 1, 'language': 'ru', 'name': 'mærd', 'registered': 0, 'status': 'user', 'telegram_id': 1242755674}, 
    'site': {'email': 'amidfox85@gmail.com', 'id': 1, 'modify_date': 'Mon, 22 Apr 2024 13:13:17 GMT', 'name': 'ivan', 'position': 1, 'surname': 'aboba', 'telegram_id': 1242755674}}
    if user.get("site"):
        result += f"""
    Информация по сайт аккаунту
Емаил - {user['site'].get("email")}
Имя - {user['site'].get("name")}
Фамилия - {user['site'].get("surname")}
        """

    await message.reply(result)


@app.on_message(filters.command("commands", prefix))  # список всех команд
async def return_all_comms(_, message) -> None:
    user_language = message.from_user.language_code
    await app.send_message(
        chat_id=message.chat.id,
        text="Тип команд",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Обычные", "default_commands"), InlineKeyboardButton("Для админов", "admin_commands"),
             InlineKeyboardButton("Все", "all_commands")],
            [InlineKeyboardButton("Выход", callback_data="exit")]])
    )
    return


@app.on_message(filters.command("me", command_prefix))  # профиль в джсоне
async def get_me(_, message) -> None:
    user = await get_user(message)
    await message.reply(f"{ta}shell\n{user}{ta}")


@app.on_message(filters.command("bash", command_prefix))  # терминал
async def get_terminal_command(_, message) -> None:
    user_language = message.from_user.language_code

    if str(message.from_user.id) != get_from_config("owner"):
        await message.reply(str(translate("func_n_a", user_language)))
        return
    command = " ".join(message.command[1:])  # message.text.split == message.command
    try:
        res = await terminal(command)
    except Exception as e:
        res = str(e)

    await message.reply(res)


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


@app.on_message(filters.command("image", prefix))  # картинки
async def draw_prompt(_, message) -> None:
    prompt = " ".join(message.command[1:])
    if prompt == '':
        await message.reply("запрос после команды напиши")
        return

    await image_menu(message, send=True)


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
    except Exception:
        result = translate("wrong_com", user_language)
    await message.reply(result)


@app.on_message(filters.command("погода", prefix))  # узнать погоду в городе
async def get_weather(_, message) -> None:
    try:
        result = weather(message.text[8:])
    except:
        result = "Неправильно написан город либо его несуществует"
    await message.reply(result)


@app.on_callback_query()
async def catch_callbacks(_, callback) -> None:
    if callback.inline_message_id is None:
        user_language = callback.message.from_user.language_code
    else:
        user_language = callback.from_user.language_code
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
        buttons = []
        if (await get_user(callback)).get("site"):
            buttons.append([InlineKeyboardButton('Отвязать аккаунты', callback_data="delete_relationship")])

        buttons.append([InlineKeyboardButton("Назад", callback_data="to_main")])

        await app.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text="Настройки сайта", reply_markup=InlineKeyboardMarkup(buttons))

    elif "delete_relationship" in callback.data:
        editing = await edit_user(data={"site": {"telegram_id": 0}}, user_id=callback.from_user.id)
        if editing:
            result = "успешно"
        else:
            result = "неполучилось"
        await callback.message.reply(result)

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
        if 'dislike' == likes[callback.inline_message_id].get(callback.from_user.id):
            likes[callback.inline_message_id][callback.from_user.id] = "nichego"
            return
        likes[callback.inline_message_id][callback.from_user.id] = 'dislike'

        await edit_inline_query_likes_buttons(callback)

    elif callback.data == "like":
        if likes.get(callback.inline_message_id) is None:
            likes[callback.inline_message_id] = dict()

        if 'like' == likes[callback.inline_message_id].get(callback.from_user.id):
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

    elif callback.data == "exit":
        # await app.edit_message_text(callback.message.chat.id,
        #                             text="ok", 
        #                             reply_markup=None,
        #                             message_id=callback.message.id)
        await app.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=[callback.message.id])

        return

    elif "image" in callback.data:
        prompt = callback.data.split(":", maxsplit=1)[1]

        if "image_draw" in callback.data:
            result = await draw(prompt, str(callback.message.id))

        if "image_search" in callback.data:
            result = await search_photo(prompt)
            # prprprpr
        await app.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=[callback.message.id])

        await app.send_photo(
            chat_id=callback.message.chat.id,
            caption="your image",
            photo=result)

    elif "calc" in callback.data:
        _, user_id, button = callback.data.split(";")

        if callback.from_user.id != int(user_id):
            return await callback.answer("Не тваи кнопки", show_alert=True, cache_time=5)

        try:
            if inline_calc_text.get(callback.inline_message_id) is None:
                inline_calc_text[callback.inline_message_id] = ""

            text = callback.message.text.split("\n")[0].strip().split("=")[0].strip() if callback.message \
                else inline_calc_text.get(callback.inline_message_id).split("\n")[0].strip().split("=")[0].strip()
            text = '' if f"Калькулятор" in text else text
            target = text + callback.data
            result = ""
            stay = False

            if button == "=":
                result = evaluate(text)
                text = ""

            elif button == "DEL":
                text = text[:-1]

            elif button == "C":
                text = ""

            elif button == "sqrt":
                result = sqrt(evaluate(text))
                stay = True

            elif button == "**2":
                text = f"{text}**2"
                result = evaluate(text)

            elif button == "**-1":
                text = f"{text}**-1"
                result = evaluate(text)

            else:
                tochki = re.findall(r"(\d*\.\.|\d*\.\d+\.)", target)
                operators = re.findall(r"([/\+-]{2,})", target)
                if not tochki and not operators:
                    if re.findall(r"(\.\d+|\d+\.\d+|\d+)", target):
                        text += button
                        result = evaluate(text)

            text = f"{result}" if stay else f"{text:<50}"
            if result:
                if text:
                    text += f"\n{result:>50}"
                else:
                    text = result
            text += f"\n\nКалькулятор {callback.from_user.first_name}"

            edit_params = {
                "text": text,
                "parse_mode": pyrogram.enums.ParseMode.DISABLED
            }

            if "inline_calc" in callback.data:
                edit_msg = app.edit_inline_text
                edit_params["inline_message_id"] = callback.inline_message_id
                markup = calc_btn(user_id, "inline_")
            else:
                edit_msg = callback.edit_message_text
                markup = calc_btn(user_id)
            edit_params["reply_markup"] = markup
            aim = text.split("\n")[0].strip().split("=")[0].strip()

            inline_calc_text[callback.inline_message_id] = aim if aim != '' else text.split("\n")[1].strip()
            await edit_msg(**edit_params)

        except Exception as error:
            print(error)

    elif "_commands" in callback.data:
        commands = await commands_list(callback.data, callback.from_user.language_code)
        await callback.edit_message_text(text=str(commands), reply_markup=None)


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
                ),
                InlineQueryResultArticle(
                    title="Калькулятор",
                    description="на кнопках",
                    input_message_content=InputTextMessageContent(f"Калькулятор {inline.from_user.first_name}"),
                    reply_markup=calc_btn(inline.from_user.id, "inline_")
                )
            ],
            cache_time=1
        )
    except Exception as e:
        if "[400 MESSAGE_EMPTY]" in str(e):
            return
        print(str(e))


@app.on_message(filters.command("calculator", prefix))  # калькулятор
async def calculate_handler(_, message):
    await message.reply(
        text=f"Калькулятор {message.from_user.first_name}",
        reply_markup=calc_btn(message.from_user.id))


@app.on_message(filters.command("send", command_prefix))  # отправить файл с диска
async def send_file_to_tg(_, message):
    try:
        name = message.text.split(" ", maxsplit=1)[1]
        if ".env" in name or 'main.py' in name:
            return await message.reply("no")
        await app.send_document(chat_id=message.chat.id,
                                document=name)
    except:
        await message.reply("some error occured")


@app.on_message(filters.command("download", command_prefix))  # скачать файл на диск
async def download_file_to_disk(_, message):
    try:
        target = message.reply_to_message
        if target is None:
            return await message.reply("команду надо ответом на сообщение с файлом")
        await app.download_media(target, block=False)
        res = "downloaded"
    except Exception as e:
        res = str(e)
    return await message.reply(res)


@app.on_message(filters.command("mute", prefix))
async def mute_user(_, message):
    pass


@app.on_message(filters.text)
@app.on_edited_message(filters.text)
async def run_code(_, message) -> None:
    if message.text.startswith("!"):
        text = message.text.split(" ", maxsplit=1)
        lang = str(text[0][1:])
        if len(text) > 1:
            code = text[1]
        else:
            code = "нету кода"
        result = await c_compile(code, lang)
        try:
            await message.reply(result)
        except MessageTooLong:
            with open("help/other/code/output.txt", "w+") as file:
                file.write(result)
            await app.send_document(chat_id=message.chat.id, document="help/other/code/output.txt")
        except MessageEmpty:
            await message.reply("no output")
        return
    return

print("bot started")
app.run()
