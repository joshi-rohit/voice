# FastAPI backend for the voice assistant
# ! pip install fastapi[all]

from fastapi import FastAPI, Request, WebSocket 
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            # data = await websocket.receive_bytes()
            # await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        print(e)
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()