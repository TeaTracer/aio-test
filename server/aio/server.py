import asyncio
import aiohttp
import ssl
import json
from aiohttp import web
from .db import Manager, RemoteManager, LocalManager
import aiohttp_debugtoolbar
from .settings import settings
from aiohttp_debugtoolbar import toolbar_middleware_factory

def get_ssl():
    """ prepare ssl context """

    key = settings["ssl"]["key"]
    crt = settings["ssl"]["crt"]
    sc = ssl.SSLContext()
    sc.load_cert_chain(crt, key)

    return sc

async def get_user(token, User):
    """ get user from request """

    if not token:
        raise HTTPForbidden()
    manager = User()
    user = await manager.verify_token(token)
    print(user)
    if not user:
        print("Wrong token")
        raise HTTPForbidden()
    return user

async def login_handler(request):
    """ handler for get login requests, respond with session token or HTTPForbidden """

    try:
        if request.method == "OPTIONS":
            print("OPTIONS")
            return web.Response()

        print('LOGIN REQUEST', request)
        login = request.headers['login']
        password = request.headers['password']
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
        headers = {'Access-Control-Allow-Origin': '*'}
        response = web.json_response(response_data, headers=headers)

    except Exception as err:
        print(err)
        raise HTTPForbidden()

    return response

async def websocket_remote_handler(request):
    print('REMOTE', request)
    token = request.match_info.get('token')
    user = await get_user(token, RemoteManager)
    print('FUSER', user)

    ws = web.WebSocketResponse()
    print("BEFORE", ws)
    print(ws.can_prepare(request))
    try:
        #  import ipdb; ipdb.set_trace()
        await ws.prepare(request)
    except Exception as err:
        print(err.args)
        raise()
    print("AFTER", ws)

    try:
        async for msg in ws:
            print(msg)
            print(msg.data)
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
                        ws.send_str(json.dumps('echo'))
                    else:
                        print(d)

            elif msg.tp == aiohttp.MsgType.error:
                print('remote ws connection closed with exception %s' %
                      ws.exception())
    except Exception as err:
        print(err.args)
        raise()

    print('remote websocket connection closed')

    return ws

async def websocket_local_handler(request):
    print('LOCAL', request)
    user = await get_user(request, LocalManager)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        print("MSSS", msg)
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                try:
                    d = json.loads(msg.data)
                    print(d)
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
    print("HELLO", request)
    return web.Response(text="Hello, world!\n")

async def init(loop):
    app = web.Application(loop=loop)
    aiohttp_debugtoolbar.setup(app)
    #  await on_startup(app)
    remote = app.router.add_resource('/api/remote/{token}')
    remote.add_route('*', websocket_remote_handler)
    local = app.router.add_resource('/api/local/{token}')
    local.add_route('*', websocket_local_handler)
    #  app.router.add_route('*', '/api/remote', websocket_remote_handler)
    #  app.router.add_route('*', '/api/local', websocket_local_handler)
    app.router.add_route('*', '/api/login/', login_handler)
    app.router.add_route('*', '/', hello_handler)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8080, ssl=get_ssl())
    print("Server started at http://0.0.0.0:8080")
    return srv, handler


loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
