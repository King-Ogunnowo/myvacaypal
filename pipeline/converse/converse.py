import datetime
import ollama
import uuid
import json

def create_conversation_id():
    return uuid.uuid4().hex

conversation_id = create_conversation_id()
converse_output_path = "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/converse/converse_output/chat_history.json"

def preserve_chat_history(messages):
    json_data = json.dumps(messages, indent=4)
    with open(converse_output_path, "w") as file:
        file.write(json_data)

def recall_chat_history():
    try:
        with open(converse_output_path, "r") as file:
            messages = json.load(file)
            return messages
        
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    

def ai_respond():
    messages = recall_chat_history()
    response = ollama.chat(
        model="gemma3",
        messages=messages
    )
    ai_reply = response['message']['content']
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply,
            "timestamp":str(datetime.datetime.now()),
        }
    )
    preserve_chat_history(messages)
    return ai_reply


def process_user_response(user_input):
    messages = recall_chat_history()
    if not messages:
        messages.append(
            {
                "role": "system",
                "content": (
                    "You are an intelligent AI travel planner assistant. "
                    "When users approach you with travel requests, do not make any assumptions. "
                    "Always ask follow-up questions to gather details. "
                    "Ask one question at a time and wait for the user's response before continuing. "
                    "As the conversation progresses, remember to keep track of the user's preferences and "
                    "interests to provide personalized recommendations. "
                    "Don't start with 'okay, xyz city seems fantastic' after your first response. "
                    "Only ask question regarding the trip, number of people travelling, duration, budget and interests, and accomodation"
                    "Once you have all the information, draw up an itenary of flight, accomodation and activities for the user"
                    "Avoid drill downs and deep dives, ask very important questions"
                    "Do not ask more than 5 questions in all"
                    "when you have all the questions you need, say this: 'Thank you for answering my questions, I will now compile your trip itenary, a minute please...'"
                    "Most importantly, ensure you get details on departure, arrival, accomodation, number of passengers, budget, activities, etc"
                    "Before you conclude the conversation, reiterate ALL the user's preference as a way of confirming the user's intent"

                ),
                "timestamp":str(datetime.datetime.now()),
                "conversation_id":conversation_id
            }
        )
    messages.append(
        {
            "role": "user",
            "content": user_input,
            "timestamp":str(datetime.datetime.now()),
        }
    )
    preserve_chat_history(messages)
    return ai_respond()
    




