from help.async_requests import Responser

requests = Responser()
lang_name = {
        "py": "python",
        "cpp": "cpp",
        "cs": "csharp",
        "js": "javascript",
        "java": "java",
        "c": "c",
        "asm": "assembly",
        "kts": "kotlin",
        "lua": "lua",
        "rs": "rust"
}


async def code_request(code, language):
    data = {"files": [{"name": f"main.{language}", "content": code}]}
    headers = {
        "content-type": "application/json",
        "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb",
    }
    type_of_language = lang_name.get(language)
    if type_of_language is None:
        type_of_language = language

    r = await requests.post(
        f"https://glot.io/api/run/{type_of_language}/latest", headers=headers, json=data
    )
    return r.json()


async def c_compile(code, language):
    try:
        if language == "languages":
            return "\n".join(lang_name)
        res = await code_request(code, language)
        result = res["stdout"] or res["stderr"]
        result = result.replace("glot", "user")
        result = f"Result :\n{result}"

    except Exception as e:
        result = str(e)

    return result
