import os

import dotenv
from vkbottle import Bot
from vkbottle.bot import Message
from vkbottle.callback import BotCallback

dotenv.load_dotenv('.env')


TOKEN = os.environ['TOKEN']
callback = BotCallback(url=os.environ['URL'], title="my server")
bot = Bot(token=TOKEN, callback=callback)


@bot.on.message(text="привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(user_ids=[message.from_id])
    await message.answer(f"Приветствую, {users_info[0].first_name}")