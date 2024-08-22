from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()


def call_openai(query: str = "") -> str:
    client = OpenAI()

    messages = [
        {"role": "user", "content": query},
    ]

    completion = client.chat.completions.create(
        temperature=0.2,
        model="gpt-4o",
        messages=messages,
    )

    res: str = completion.choices[0].message.content
    return res
