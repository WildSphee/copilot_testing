import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


luisbot = {"init": os.getenv("COPILOT_INIT"), "chat": os.getenv("COPILOT_CHAT")}


def copilot_init(url):
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during initialization: {e}")
        return None


def copilot_chat(url, token, conversation_id, message):
    if token and conversation_id:
        try:
            start_time = time.time()
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "token": token,
                    "conversationId": conversation_id,
                    "message": message,
                },
            )
            response.raise_for_status()
            end_time = time.time()
            return response.json(), end_time - start_time
        except requests.exceptions.RequestException as e:
            print(f"Error during chat: {e}")
            return None, None
    else:
        print("Invalid copilot request")
        return None, None


def get_copilot_response(url, token, watermark=0):
    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        data = response.json()
        data["currentwatermark"] = watermark
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error getting response: {e}")
        return None


def process_responses(request_link, token, watermark):
    index = 0
    count = 0
    text = ""
    while count <= 300:
        response_msg = get_copilot_response(request_link, token, watermark)
        if response_msg and watermark == response_msg["currentwatermark"]:
            activities = response_msg.get("activities", [])
            while index < len(activities):
                msg = activities[index]
                if msg.get("type") == "message":
                    if "text" in msg:
                        print("Text:", msg["text"])
                        text += msg["text"]
                        count = 1000
                index += 1
            count += 1
            time.sleep(0.1)
        else:
            break

    return text


def create_one_chat_compl(
    query: str = "what is the singtel code of conduct?",
) -> tuple[str, float]:
    """
    main entry point

    attribute:
        query (str): question for Luis Copilot

    return:
        str: the final result
        float: time taken for chat completion
    """

    init_response = copilot_init(luisbot["init"])
    if init_response:
        token = init_response.get("token")
        conversation_id = init_response.get("conversationid")

        # Chat
        message = query
        chat_response, chat_time = copilot_chat(
            luisbot["chat"], token, conversation_id, message
        )

        if chat_response:
            request_link = chat_response.get("request_link")
            watermark = 0
            start = time.time()
            res = process_responses(request_link, token, watermark)
            total_time = (
                time.time() - start - 0.05
            )  # offset for timer, as we capture the latest response in every 0.1s, average delay between response and capture is 0.05s

    return res, total_time
