import os
import requests
import base64

import dto
import dotenv

from datetime import datetime
from vkbottle import GroupEventType
from vkbottle.bot import Bot, Message, MessageEvent
from vkbottle.callback import BotCallback

from dto import SendPlaceInfoResponse

dotenv.load_dotenv('.env')

TOKEN = os.environ['TOKEN']
BACKEND_URL = os.environ['BACKEND_URL']

callback = BotCallback(url=os.environ['URL'], title='vk-bot-adapter')
bot = Bot(token=TOKEN, callback=callback)


@bot.on.message()
async def message_and_command_handler(message: Message):

    if message.text.startswith('/'):
        cmd = dto.Command(
            user_id=str(message.from_id),
            date_time=datetime.fromtimestamp(message.date).isoformat(),
            name=message.text[1:],
            place=dto.SendPlaceInfoRequest(
                chat_id=str(message.peer_id),
            )
        )

        requests.post(
            url=f'{BACKEND_URL}/command',
            json=cmd.model_dump(),
        )

    else:
        if message.text != '':
            msg = dto.Message(
                user_id=str(message.from_id),
                text=message.text,
                place=dto.SendPlaceInfoRequest(
                    chat_id=str(message.peer_id),
                ),
            )
            requests.post(
                url=f'{BACKEND_URL}/user_message',
                json=msg.model_dump(),
            )
        if message.attachments is not None and len(message.attachments) > 0:

            attachments_base64 = []
            for photo in message.get_photo_attachments():
                photo_file = requests.get(photo.sizes[-4].url)
                attachments_base64.append(base64.b64encode(photo_file.content))

            images = dto.Image(
                user_id=str(message.from_id),
                place=dto.SendPlaceInfoRequest(
                    chat_id=str(message.peer_id),
                ),
                attachments_base64=attachments_base64,
                date_time=datetime.fromtimestamp(message.date).isoformat()
            )

            requests.post(
                url=f'{BACKEND_URL}/image',
                json=images.model_dump(),
            )



@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def keyboard_input_handler(event: MessageEvent):
    enter_keyboard = dto.EnterKeyboard(
        user_id=str(event.user_id),
        button=event.payload.get('cmd'),
        date_time=datetime.now().isoformat(),
        place=SendPlaceInfoResponse(
            chat_id=str(event.peer_id),
            message_id=''
        )
    )

    requests.post(
        url=f'{BACKEND_URL}/keyboard/input',
        json=enter_keyboard.model_dump(),
    )

    await event.send_empty_answer()
