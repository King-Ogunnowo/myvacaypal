import ollama
import json
import ast

conversation_history_path = "../converse/converse_output/chat_history.json"

def load_chat_history(conversation_history_path):
    with open(conversation_history_path, 'r') as file:
        data = json.load(file)
    result = [i['content'] for i in data if i['role'] == 'user']
    return result

def process_chat_history(conversation_history_path):
    chat_history = load_chat_history(conversation_history_path)
    message = [{
            "role": "system",
            "content": (
                "You are an intelligent AI travel entity extraction assistant "
                "This is a conversation between an AI model and a human about a trip the human wishes to go on."
                "The model through questions has made the user indicate the desires of the user."
                "In the users responses lies some important responses concerning their transportation, accomodation and activities"
            ),
            "temperature":-1
        },
        {
            "role":"system",
            "content":f"""extract the entities from the text into a python dictionary containing key value pairs, where the key is the enetity name and the value is the extracted entity"

                
                departure_date:"YYYY-MM-DD departure date",
                return_date:"YYYY-MM-DD arrival date",
                budget:"budget for the trip",
                n_travellers:"number of travellers",
                n_adults:"number of adults",
                n_children:"number of children",
                "interests":"interests of the user",
                destination: "destination of the user",
                departure: "city of departure of the user"
                
                here is the chat: {chat_history}

                The interests part is very important because that will help us book the right activities for the trip
                Also extract rightly the number of adults and number of children and the number of travellers
                stick to this format, do not deviate even the slightest
                split the trip dates into arrival date and departure date
                if an entity is not present in the text, return None as the value in your output
                Make sure you extract every preference of the user as an entity
                DO NOT EXTRACT WHAT IS NOT PRESENT IN THE CONVERSATION. IF YOU ARE UNSURE, DO NOT EXTRACT IT!!!
                IF THERE IS ONLY A SINGLE TRAVELLER, WE CAN ASSUME THE PERSON IS AN ADULT UNLESS THEY SPECIFY OTHERWISE.
                ENSURE THE DATES FOLLOWS THIS FORMAT: 
                Output only the python dictionary.

                Output:"""
        }]
    
    response = ollama.chat(
        model = "gemma3",
        messages = message
    )

    entities = response['message']['content']
    
    return entities

def process_output(entities):
    cleaned = entities.replace("```python", "").replace("```", "")
    cleaned = ast.literal_eval(cleaned)
    return cleaned

def save_entities():
    entities = process_chat_history(conversation_history_path)
    entities = process_output(entities)
    with open("entity_extraction_output/entities.json", "w") as f:
        json.dump(entities, f, indent=4)

if __name__ == "__main__":
    save_entities()