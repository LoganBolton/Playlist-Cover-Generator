import os 
import base64
import requests
import anthropic

# Claude
def set_up_claude():
    api_key = os.environ.get("ANTHROPIC_API_KEY_PERSONAL")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        exit(1)

    # Set up the client
    client = anthropic.Anthropic(api_key=api_key)
    
def get_conversation(prompt):
    message = [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ]
                }]
    return message

def send_message(conversation):
    message = anthropic.Anthropic().messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=conversation
    )
    # print(f"response to followup: {message.content}")
    pure_text = message.content[0].text
    # print(f"pure text: {pure_text}")
    return pure_text

def extract_description(text):
    start = text.index('[') + 1
    end = text.index(']')
    result = text[start:end]
    return result