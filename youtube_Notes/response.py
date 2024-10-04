import os
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def send(
    prompt=None,
    text_data=None,
    chat_model="gpt-3.5-turbo-0125",
    model_token_limit=8192,
    max_tokens=2500,
):

    if not prompt:
        return "Error: Prompt is missing. Please provide a prompt."
    if not text_data:
        return "Error: Text data is missing. Please provide some text data."

    tokenizer = tiktoken.encoding_for_model(chat_model)

    token_integers = tokenizer.encode(text_data)

    chunk_size = max_tokens - len(tokenizer.encode(prompt))
    chunks = [
        token_integers[i : i + chunk_size]
        for i in range(0, len(token_integers), chunk_size)
    ]

    chunks = [tokenizer.decode(chunk) for chunk in chunks]

    responses = []
    messages = [
        {"role": "system",
         "content": "first of all dont generate nested values You are a study material creator bot which will convert the given text into easy to understand and beginner friendly material sample output is {'Introduction to Expo': 'Expo is a programming language'} like this and dont output nested values for the content write everything in the , dont include single quotes and you will generate easy to understand study materials and explain it to them like they are beginners for the text provided by user and strictly follow the format and and output JSON"},
        {"role": "user", "content": prompt},
        {
            "role": "user",
            "content": "To provide the context for the above prompt, I will send you text in parts. When I am finished, I will tell you 'ALL PARTS SENT'. Do not answer until you have received all the parts.",
        },
    ]

    for chunk in chunks:
        messages.append({"role": "user", "content": chunk})

        while (
            sum(len(tokenizer.encode(msg["content"])) for msg in messages)
            > model_token_limit
        ):
            messages.pop(1)

        response = client.chat.completions.create(model=chat_model, response_format={"type": "json_object"}, messages=messages)
        chatgpt_response = response.choices[0].message.content
        responses.append(chatgpt_response)

    messages.append({"role": "user", "content": "ALL PARTS SENT"})
    response = client.chat.completions.create(model=chat_model, response_format={"type": "json_object"}, messages=messages)
    final_response = response.choices[0].message.content
    responses.append(final_response)
    responses.pop(0)
    return responses
