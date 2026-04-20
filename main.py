import dto

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from vkbottle import Keyboard, Callback

from mangum import Mangum

from bot import bot
from fastapi import Response, Request

confirmation_code: str
secret_key: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    global confirmation_code, secret_key
    confirmation_code, secret_key = await bot.setup_webhook()
    yield


app = FastAPI(lifespan=lifespan)


@app.post('/')
async def vk_handler(req: Request):
    try:
        data = await req.json()
    except Exception:
        return Response(status_code=400)

    print(data)

    if data['type'] == 'confirmation':
        return Response(content=confirmation_code)
    await bot.process_event(data)

    return Response(content='ok')


@app.post('/keyboard/create')
async def create_keyboard(keyboard_request: dto.KeyboardRequest):
    try:
        keyboard = Keyboard(one_time=False, inline=False)

        for btn in keyboard_request.buttons:
            keyboard.add(Callback(btn.text, payload={'cmd': btn.text}))

        result = await bot.api.messages.send(
            user_id=int(keyboard_request.user_id),
            random_id=0,
            peer_id=int(keyboard_request.place.chat_id),
            message=keyboard_request.title,
            keyboard=keyboard.get_json(),
        )

        message_id = str(result) if isinstance(result, int) else str(result[0]) if result else ''

        return dto.KeyboardResponse(
            user_id=keyboard_request.user_id,
            place=dto.SendPlaceInfoResponse(
                chat_id=keyboard_request.place.chat_id,
                message_id=message_id,
            ),
            date_time=datetime.now().isoformat(),
        )
    except Exception as e:
        return Response(
            status_code=500,
            content=dto.Error(code=500, message=str(e)).model_dump_json(),
            media_type='application/json',
        )


@app.post('/keyboard/update')
async def update_keyboard(keyboard_request: dto.KeyboardRequestUpdate):
    try:
        keyboard = Keyboard(one_time=False, inline=False)

        for btn in keyboard_request.buttons:
            keyboard.add(Callback(btn.text, payload={'cmd': btn.text}))

        await bot.api.messages.send(
            user_id=int(keyboard_request.user_id),
            random_id=0,
            peer_id=int(keyboard_request.place.place.chat_id),
            message=keyboard_request.title,
            keyboard=keyboard.get_json(),
        )

        return Response(content='ok')
    except Exception as e:
        return Response(
            status_code=500,
            content=dto.Error(code=500, message=str(e)).model_dump_json(),
            media_type='application/json',
        )


@app.post('/message')
async def send_message(message: dto.Message):
    try:
        result = await bot.api.messages.send(
            user_id=int(message.user_id),
            random_id=0,
            peer_id=int(message.place.chat_id),
            message=message.text,
        )

        message_id = str(result) if isinstance(result, int) else str(result[0]) if result else ''

        return dto.SendPlaceInfoRequestWithMessage(
            user_id=message.user_id,
            place=dto.SendPlaceInfoResponse(
                chat_id=message.place.chat_id,
                message_id=message_id,
            ),
            date_time=message.date_time,
        )
    except Exception as e:
        return Response(
            status_code=500,
            content=dto.Error(code=500, message=str(e)).model_dump_json(),
            media_type='application/json',
        )

@app.get('/health-check')
async def check_health():
    return Response(status_code=200, content='ok')

handler = Mangum(app)