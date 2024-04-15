from .async_requests import Responser


import asyncio
import json

requests = Responser()


async def python_compile(code):
    data = {"files": [{"name": f"maerd.py", "content": code}]}
    headers = {
        "content-type": "application/json",
        "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb",
    }
    r = await requests.post(
        f"https://glot.io/api/run/{lang}/latest", headers=headers, json=data
    )
    return await r.json()


@app.on_message(filters.command("python", command_prefix))
@app.on_edited_message(filters.command("python", command_prefix))
async def python(client, message):
    if len(message.command) < 2:
        await message.reply("пиши код ало")
        return

    res = await python_compile(" ".join(message.text.split(" ", maxsplit=1)[1]))

    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"

    try:
        return await message.reply(hasil)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e)