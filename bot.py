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
HEADERS = {'X-Connector-Name': 'vk'}

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
            headers=HEADERS,
        )

    else:
        if message.text != '':
            msg = dto.Message(
                user_id=str(message.from_id),
                text=message.text,
                place=dto.SendPlaceInfoRequest(
                    chat_id=str(message.peer_id),
                ),
                date_time=datetime.fromtimestamp(message.date).isoformat(),
            )
            requests.post(
                url=f'{BACKEND_URL}/user_message',
                json=msg.model_dump(),
                headers=HEADERS,
            )
        if message.attachments is not None and len(message.attachments) > 0:

            attachments_base64 = []
            photo_attachments = message.get_photo_attachments()
            if photo_attachments:
                for photo in photo_attachments:
                    if photo.sizes and len(photo.sizes) >= 4:
                        photo_url = photo.sizes[-4].url
                        if photo_url:
                            photo_file = requests.get(photo_url)
                            attachments_base64.append(base64.b64encode(photo_file.content))

            if attachments_base64:
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
                    headers=HEADERS,
                )



@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def keyboard_input_handler(event: MessageEvent):
    button_value = event.payload.get('cmd') if event.payload else None
    if button_value is None:
        return

    enter_keyboard = dto.EnterKeyboard(
        user_id=str(event.user_id),
        button=button_value,
        date_time=datetime.now().isoformat(),
        place=SendPlaceInfoResponse(
            chat_id=str(event.peer_id),
            message_id=''
        )
    )

    requests.post(
        url=f'{BACKEND_URL}/keyboard/input',
        json=enter_keyboard.model_dump(),
        headers=HEADERS,
    )

    await event.send_empty_answer()
