# FastAPI backend for the voice assistant
# ! pip install fastapi[all]

from fastapi import FastAPI, Request, WebSocket 
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Callable

from deepgram import  (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        deepgram_socket = await process_audio(websocket)
        while True:
            #data = await websocket.receive_text()
            data = await websocket.receive_bytes()
            #print("data received: ")
            await deepgram_socket.send(data)
            """
            if 'channel' in data:
                transcript = data['channel']['alternatives'][0]['transcript']

                if transcript:
                    await websocket.send_text(f"Message text was: {transcript}")
            """
    except Exception as e:
        print(e)
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()
        await deepgram_socket.finish()

"""
async def process_audio(fast_socket: WebSocket):
    async def get_transcript(data: Dict) -> None:
        if 'channel' in data:
            transcript = data['channel']['alternatives'][0]['transcript']

            if transcript:
                await fast_socket.send_text(transcript)

    deepgram_socket = await connect_to_deepgram(get_transcript)

    return deepgram_socket


async def connect_to_deepgram(transcript_received_handler: Callable[[Dict], None]):
    try:
        # open the DeepgramClient transcription socket
        socket = await deepgram.transcription.live({'punctuate': True, 'interim_results': False})
        # register two event handlers
        socket.registerHandler(socket.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))
        socket.registerHandler(socket.event.TRANSCRIPT_RECEIVED, transcript_received_handler)

        return socket
    except Exception as e:
        raise Exception(f'Could not open socket: {e}')
"""
#config = DeepgramClientOptions(options={"keepalive": "true"})
#dg_client = DeepgramClient(os.getenv('DEEPGRAM_API_KEY'), config)

async def process_audio(fast_socket: WebSocket):
    async def message_handler(data: Dict) -> None:
        """Listen and Print the transcription"""
        sentence = data.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        print(f"Transcription: {sentence}")
        return fast_socket.send_bytes(sentence)

    deepgram_socket = await connect_to_deepgram(message_handler)

    return deepgram_socket
async def connect_to_deepgram(message_handler: Callable[[Dict], None]):
    try:
        # Configure the DeepgramClientOptions to enable KeepAlive for maintaining the WebSocket connection (only if necessary to your scenario)
        config = DeepgramClientOptions(options={"keepalive": "true"})
        # Create a websocket connection using the DEEPGRAM_API_KEY from environment variables
        deepgram = DeepgramClient(os.getenv('DEEPGRAM_API_KEY'), config)
        # Use the listen.live class to create the websocket connection
        dg_connection = deepgram.listen.asyncwebsocket.v("1")
        print ("Listening...")
        
        async def on_error(self, error, **kwargs):
            """Listen and Print the error"""
            print(f"Error: {error}")

        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Transcript, message_handler)

        # connect to the Deepgram websocket server
        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=300,
            smart_format=True,
        )

        dg_connection.start(options)
        return dg_connection
    except Exception as e:
        #print(f"Could not open Deepgram socket: {e}")
        raise Exception(f'Could not open Deepgram socket: {e}')
        return
