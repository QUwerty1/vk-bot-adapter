import dto

from contextlib import asynccontextmanager
from fastapi import FastAPI
from vkbottle import Keyboard, Callback

from bot import bot
from fastapi import Response, Request

confirmation_code: str
secret_key: str

@asynccontextmanager
async def lifespan(_: FastAPI):
    global confirmation_code, secret_key
    confirmation_code, secret_key = await bot.setup_webhook()
    yield

app = FastAPI(lifespan=lifespan, port=5000)


@app.post('/')
async def vk_handler(req: Request):
    try:
        data = await req.json()
    except Exception:
        return Response(status_code=400)

    print(data)

    if data['type'] == 'confirmation':
        return Response(confirmation_code)
    await bot.process_event(data)

    return Response('ok')


@app.post('/keyboard/create')
def create_keyboard(keyboard_request: dto.KeyboardRequest):

    keyboard = Keyboard(one_time=False, inline=False)

    for btn in keyboard_request.buttons:
        keyboard.add(Callback(btn.text, payload={'cmd': btn.text}))

    bot.api.messages.send(
        user_id=keyboard_request.user_id,
        random_id=0,
        peer_id=keyboard_request.place.chat_id,
        message=keyboard_request.title,
        keyboard=keyboard.get_json(),
    )


@app.post("/keyboard/update")
def update_keyboard(keyboard_request: dto.KeyboardRequestUpdate):
    keyboard = Keyboard(one_time=False, inline=False)

    for btn in keyboard_request.buttons:
        keyboard.add(Callback(btn.text, payload={'cmd': btn.text}))

    bot.api.messages.send(
        user_id=keyboard_request.user_id,
        random_id=0,
        peer_id=keyboard_request.place.place.chat_id,
        message=keyboard_request.title,
        keyboard=keyboard.get_json(),
    )


@app.post('/message')
def send_message(message: dto.Message):
    bot.api.messages.send(
        user_id=message.user_id,
        random_id=0,
        peer_id=message.place.chat_id,
        message=message.text,
    )
