import httpx


class Responser:
    def __init__(self):
        self.ok = False

    async def get(self, url, params=None):
        async with httpx.AsyncClient() as session:
            response = await session.get(url, params=params)
            self.okkk(response.status_code)
            return response

    async def post(self, url, json=None, params=None, headers=None):
        async with httpx.AsyncClient() as session:
            response = await session.post(url, json=json, params=params, headers=headers)
            self.okkk(response.status_code)
            return response

    async def put(self, url, json=None, params=None):
        async with httpx.AsyncClient() as session:
            response = await session.put(url, json=json, params=params)
            self.okkk(response.status_code)
            return response

    async def delete(self, url, params=None):
        async with httpx.AsyncClient() as session:
            response = await session.delete(url, params=params)
            self.okkk(response.status_code)
            return response

    def okkk(self, status):
        self.ok = True if status == 200 else False

# example
# result = await get_response("http://127.0.0.1:5000/", "get")
