from fastapi import FastAPI
from dto import *
import uuid

app = FastAPI(
    servers=[{"url": "http://localhost:8000"}]
)

keyboard_storage = []
message_storage = []
image_storage = []
command_storage = []


@app.post("/keyboard/input", tags=["API's коннектора"])
async def enter_keyboard(request: EnterKeyboard):
    keyboard_data = {
        "id": str(uuid.uuid4()),
        "user_id": request.user_id,
        "button": request.button,
        "place": request.place.model_dump(),
        "date_time": request.date_time,
        "received_at": datetime.now().isoformat()
    }
    keyboard_storage.append(keyboard_data)

    print(keyboard_data)

    return {"status": "success", "message": "Keyboard input received"}


@app.post("/image", tags=["API's коннектора"])
async def send_images(request: Image):
    image_count = len(request.attachments_base64)
    attachment_urls = [
        f"https://example/images/{uuid.uuid4()}.jpg"
        for _ in range(image_count)
    ]
    image_data = {
        "user_id": request.user_id,
        "image_count": image_count,
        "attachment_urls": attachment_urls,
    }
    image_storage.append(image_data)

    print(image_data)

    return ImageURL(attachment_urls=attachment_urls)


@app.post("/command", tags=["API's коннектора"])
async def send_command(request: Command):
    command_data = {
        "user_id": request.user_id,
        "command_name": request.name,
        "place": request.place.model_dump(),
    }
    command_storage.append(command_data)

    print(command_data)

    if request.name == "start":
        return {"status": "success", "message": "Bot started"}
    elif request.name == "stop":
        return {"status": "success", "message": "Bot stopped"}
    else:
        return {"status": "success", "message": f"Command '{request.name}' executed"}


@app.post("/user_message", tags=["API's коннектора"])
async def send_message_from_module(request: Message):
    message_data = {
        "user_id": request.user_id,
        "text": request.text,
        "place": request.place.model_dump(),
    }
    message_storage.append(message_data)

    print(f"Received user message: {message_data}")

    return {"status": "success", "message": "User message received"}


# Эндпоинты для (для отладки)
@app.get("/debug/keyboard_inputs", tags=["Debug"])
async def get_keyboard_inputs():
    """Получить все полученные данные о нажатиях клавиатуры"""
    return {"keyboard_inputs": keyboard_storage}


@app.get("/debug/images", tags=["Debug"])
async def get_images():
    """Получить все полученные данные об изображениях"""
    return {"images": image_storage}


@app.get("/debug/commands", tags=["Debug"])
async def get_commands():
    """Получить все полученные команды"""
    return {"commands": command_storage}


@app.get("/debug/user_messages", tags=["Debug"])
async def get_user_messages():
    """Получить все полученные сообщения от пользователей"""
    return {"user_messages": message_storage}
