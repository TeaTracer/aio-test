import asyncio
import aiohttp
from aiohttp import web
from .db import Manager, RemoteManager, LocalManager
import aiohttp_debugtoolbar
from aiohttp_debugtoolbar import toolbar_middleware_factory


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

    ws = web.WebSocketResponse()
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

    ws = web.WebSocketResponse()
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

async def on_startup(app):
    manager = LocalManager()
    await manager.create_all()
    await manager.get_starter_pack()

def hello_handler(request):
    print(request)
    return web.Response(text="Hello, world!\n")

async def init(loop):
    app = web.Application(loop=loop)
    aiohttp_debugtoolbar.setup(app)
    app.on_startup.append(on_startup)
    app.router.add_route('*', '/remote', websocket_remote_handler)
    app.router.add_route('*', '/local', websocket_local_handler)
    app.router.add_route('*', '/login', login_handler)
    app.router.add_route('*', '/', hello_handler)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8080)
    print("Server started at http://0.0.0.0:8080")
    return srv, handler


loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
