import asyncio
import aiohttp
from .db import Manager, RemoteManager, LocalManager

async def get_user(request, User):
    """ get user from request """

    user = None
    if hasattr(request, 'cookies'):
        token = request.cookies.get("token", None)
        if not token:
            print("Cookies without token field")
            raise HTTPForbidden()
        manager = User()
        user = await manager.verify_token(token)
        if not user:
            print("Wrong token")
            raise HTTPForbidden()
    else:
        print("Request without cookies")
        raise HTTPForbidden()
    return user

async def login_handler(request):
    data = await request.post()
    login = data['login']
    password = data['password']
    manager = RemoteManager()
    uid = await manager.verify_credentials(login, password)
    if not uid:
            print("Wrong credentials")
            raise HTTPForbidden()
    token = await manager.create_token(uid)
    if not token:
            print("Wrong token creation")
            raise HTTPForbidden()

    response_data = {"token": token}
    return web.json_response(response_data)

async def websocket_remote_handler(request):
    user = await get_user(request, RemoteManager)

    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                try:
                    d = json.loads(msg.data)
                except Exception as err:
                    print(err)
                    raise HTTPForbidden()
                method = d.get('method', None)
                data = d.get('data', None)
                if method == 'echo':
                    ws.send_str(data)
                else:
                    print(d)

        elif msg.tp == aiohttp.MsgType.error:
            print('remote ws connection closed with exception %s' %
                  ws.exception())

    print('remote websocket connection closed')

    return ws

async def websocket_local_handler(request):
    user = await get_user(request, LocalManager)

    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                try:
                    d = json.loads(msg.data)
                except Exception as err:
                    print(err)
                    raise HTTPForbidden()
                method = d.get('method', None)
                data = d.get('data', None)
                if method == 'echo':
                    ws.send_str(data)
                else:
                    print(d)

        elif msg.tp == aiohttp.MsgType.error:
            print('local ws connection closed with exception %s' %
                  ws.exception())

    print('local websocket connection closed')

    return ws

loop = asyncio.get_event_loop()
loop.run_until_complete(LocalManager().get_starter_pack())
app = aiohttp.web.Application(loop=loop)
app.router.add_route('*', '/remote', websocket_remote_handler)
app.router.add_route('*', '/local', websocket_local_handler)
app.router.add_route('*', '/login', login_handler)
