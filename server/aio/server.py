import asyncio
import aiohttp

async def websocket_handler(request):
    print('REQUEST HEADERS: ', request.headers)
    if hasattr(request, 'cookies'):
        print('REQUEST COOKIES: ', request.cookies)
    else:
        print('NO COOKIES: ')


    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                ws.send_str(msg.data)
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws

loop = asyncio.get_event_loop()
app = aiohttp.web.Application(loop=loop)
app.router.add_route('*', '/', websocket_handler)
