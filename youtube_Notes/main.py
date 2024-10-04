import os

import uvicorn
from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic import BaseModel
from dotenv import load_dotenv
import json
from response import send
from fastapi.middleware.cors import CORSMiddleware
from pytube import extract

load_dotenv()




async def fetch_transcript(video_id: str) -> str:
    transcript = ""
    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    for item in transcript_data:
        transcript += item["text"] + " "
    transcript = transcript.strip()
    return transcript


# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# safety_settings = [
#     {
#         "category": "HARM_CATEGORY_DANGEROUS",
#         "threshold": "BLOCK_NONE",
#     },
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_NONE",
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_NONE",
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_NONE",
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_NONE",
#     },
# ]

# GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
# chat = model.start_chat(history=[])

# def to_markdown(text):
#     text = text.replace('•', '  *')
#     return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# def clean_response(response_text):
#     response_text = response_text.replace('```python', '')
#     return response_text.replace('```', '')


# async def send_message_and_get_response(message):
#     future = asyncio.get_running_loop().create_future()
#     await wait_for_response(future, message)
#     return await future


# async def wait_for_response(future, message):
#     result = chat.send_message(message)
#     future.set_result(
#         result.text.strip().replace('\n', ' ').replace("```python", "").replace("```", "").replace("*", " ").replace(
#             "-", " "))
#
# load_dotenv()

# async def summarize_video(transcript):
#     CHUNK_SIZE = 10
#     chapters = {}
#
#     async def process_chunk(chunk_index, chunk_text):
#         user_message = f"I am going to give you 10 chunks of video transcript create " \
#                        f"them into easy to understand texts " \
#                        f"and don't include \n or single or double quotes or any other " \
#                        f"characters other than alphabets " \
#                        f"here is the {'first' if chunk_index == 0 else 'next'} part of the text: {chunk_text}"
#         model_response = await send_message_and_get_response(user_message)
#
#         if chunk_index != 0:
#             user_message = f"Now make an easy-to-understand text from this too and don't " \
#                            f"include \n or single or double quotes or any other character " \
#                            f"other than alphabets: {chunk_text}"
#             model_response += " " + await send_message_and_get_response(user_message)
#
#         return model_response
#
#     tasks = [
#         process_chunk(i, transcript[i * (len(transcript) // CHUNK_SIZE): (i + 1) * (len(transcript) // CHUNK_SIZE)]) for
#         i in range(CHUNK_SIZE)]
#     summaries = await asyncio.gather(*tasks)
#
#     for i, summary in enumerate(summaries):
#         chapters[f"Chapter {i + 1}"] = summary
#
#     return chapters
#

class Url(BaseModel):
    url: str


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "This is a get request make a post request for generating study material"}


@app.post("/")
async def generate_material(url: Url):
    video_id = extract.video_id(url.url)
    transcript = await fetch_transcript(video_id)
    responses = send(prompt=f"generate study material for the given text: ", text_data=transcript)
    parsed_responses = []

    for response in responses:
        parsed_response = json.loads(response)
        parsed_responses.append(parsed_response)
    return parsed_responses

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)