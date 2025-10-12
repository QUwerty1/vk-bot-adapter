from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import bot
from fastapi import Response, Request, BackgroundTasks

confirmation_code: str
secret_key: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    global confirmation_code, secret_key
    confirmation_code, secret_key = await bot.setup_webhook()
    yield

app = FastAPI(lifespan=lifespan, port=5000)


@app.post("/")
async def vk_handler(req: Request, background_task: BackgroundTasks):
    try:
        data = await req.json()
    except Exception:
        return Response("not today", status_code=403)

    print(data)
    if data["type"] == "confirmation":
        return Response(confirmation_code)

    # If the secrets match, then the message definitely came from our bot
    if data["secret"] == secret_key:
        # Running the process in the background, because the logic can be complicated
        background_task.add_task(bot.process_event, data)
    return Response("ok")
