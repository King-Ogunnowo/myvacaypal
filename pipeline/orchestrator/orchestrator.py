import subprocess
import ollama
import json


tasks = {
    "flight_booking": "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/flight_search/flight_search.py",
    "hotel_booking": "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/hotel_search/hotel_search.py"
}

conversation_path = "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/converse/converse_output/chat_history.json"

def recall_chat_history(conversation_path):
    try:
        with open(conversation_path, "r") as file:
            messages = json.load(file)
            return messages
        
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    
def run_task(identified_tasks):
    identified_tasks = identified_tasks.split(', ')
    subprocess.run(["python", "/Users/oluwaseyi/Documents/repositories/myvacaypal/update_access_token.py"])
    subprocess.run(["python", "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/entity_extraction/entity_extraction.py"])
    for task in identified_tasks:
        script = tasks[task]
        subprocess.run(["python", script])
    

def choose_tasks():

    conversation = recall_chat_history(conversation_path)

    messages = [{
        "role":"system",
        "content": (
            "You are an intelligent Natural Language Understanding model working as part of a team currently building and maintaining an AI travel planning assistant"
            "You have recieved conversations between an AI system and a user who wishes to plan a trip."
            "You are to make a decision on which tasks the this software needs to achieve based on the conversation you observe."
            f"The user through requests or responses might hint at any or all of the following objectives/ tasks: {list(tasks.keys())}."
            "Your task is to understand the user request and decipher which task they need to be achieved."
            "In your output return only the task, nothing else"
            "an example: 'flight_booking"

            "It is also possible that the tasks that need to be achieved include a combination of tasks. An example output: 'flight_booking, hotel_booking'"

            f"here is the conversation: {conversation}"

            "Output:"
        )
    }]

    response = ollama.chat(
        model = "gemma3",
        messages = messages
    )

    identified_tasks = response['message']['content']
    run_task(identified_tasks)
