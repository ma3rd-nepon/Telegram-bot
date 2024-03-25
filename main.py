from pyrogram import *
from other.utils import *


prefix = "/"
command_prefix = get_from_config("prefix")

api_id = get_from_config("api_id")
app = Client(name=get_from_config("name"), 
             api_id=api_id,
             api_hash=get_from_config("api_hash"),
             bot_token=get_from_config("bot_token"),
             )


@app.on_message(filters.command("start", prefix))
async def start_function(client, message):
    user_id, name = message.from_user.id, message.from_user.first_name
    user = user_in_db(user_id)
    if user:
        await message.reply("Glad to see u, {}".format(user))
    else:
        add_user(user_id, name)
        await message.reply("Hello, {}, u are my new user!".format(name))
        return


@app.on_message(filters.command("name", prefix))
async def change_name_in_db(client, message):
    user_id = message.from_user.id
    if len(message.text.split(" ")) >= 2:
        new_name = str(message.text.split(" ", maxsplit=1)[1])
    else:
        await message.reply("Write new name after command!")
        return
    if user_in_db(user_id):
        pass
    else:
        add_user(user_id, message.from_user.first_name)
    
    for i in new_name:
        if i.lower() not in "1234567890-=qwertyuiop[]asdfghjkl;'zxcvbnm, йцукенгшщзхъфывапролджэячсмитьбю":
            await message.reply("Dont use strange symbols in your name!")
            return
    edit_user(user_id, new_name)
    await message.reply("Nice! Now I'm going to call you {}".format(new_name))
    return

print("bot started work")
app.run()
