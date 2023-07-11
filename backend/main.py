# uvicorn main:app --reload

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai
from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.database import store_messages, reset_messages
from functions.text_to_speech import convert_text_to_speech

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:3000",
    "https://whybee-chat.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def check_health():
    return {"message": "healthy"}

@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"message": "conversation reset"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):

    audio_input = open("voice.mp3", "rb")

    #with open(file.filename, "wb") as buffer:
    #    buffer.write(file.file.read())
    #audio_input = open(file.filename, "rb")

    print('1. audio_input')
    print(audio_input)
        
    message_decoded = convert_audio_to_text(audio_input)

    print('2. message_decoded')
    print(message_decoded)

    if not message_decoded:
        return HTTPException(status_code=400, detail="Failed to decode audio")

    chat_response = get_chat_response(message_decoded)

    print('3. chat_response')
    print(chat_response)

    if not chat_response:
        return HTTPException(status_code=400, detail="Failed to get chat response")

    store_messages(message_decoded, chat_response)

    audio_output = convert_text_to_speech(chat_response)

    if not audio_output:
        return HTTPException(status_code=400, detail="Failed to get Eleven Labs audio response")
    
    def iterfile():
        yield audio_output

    return StreamingResponse(iterfile(), media_type="application/octet-stream")

# @app.post("/post-audio/")
# async def post_audio(file: UploadFile = File(...)):
#     print("hello")
