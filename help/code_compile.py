from pyrogram.errors import MessageTooLong
from help.async_requests import Responser

requests = Responser()


async def code_request(code, language):
    data = {"files": [{"name": f"main.{language}", "content": code}]}
    headers = {
        "content-type": "application/json",
        "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb",
    }
    r = await requests.post(
        f"https://glot.io/api/run/{language}/latest", headers=headers, json=data
    )
    return r.json()


async def python_compile(code, language):
    try:
        res = await code_request(code, language)
        result = res["stdout"] or res["stderr"]
        result = result.replace("glot", "user")
        result = f"Result :\n{result}"

    except MessageTooLong:
        # pochinit
        result = f"sended to pastebin"
    except Exception as e:
        result = str(e)

    return result
