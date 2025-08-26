from openai import OpenAI
import json
import math
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def calculate_circle_area(radius):
    return math.pi * radius ** 2

def calculate_square_area(side):
    return side ** 2

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_circle_area",
            "description": "Calculate area of a circle",
            "parameters": {
                "type": "object",
                "properties": {
                    "radius": {"type": "number", "description": "Radius of the circle"}
                },
                "required": ["radius"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "calculate_square_area",
            "description": "Calculate area of a square",
            "parameters": {
                "type": "object",
                "properties": {
                    "side": {"type": "number", "description": "Side length of the square"}
                },
                "required": ["side"]
            }
        }
    }
]

def run_agent():
    messages = [
        {"role": "user", "content": "What is the area of a circle with radius 5?"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "calculate_circle_area":
                result = calculate_circle_area(arguments["radius"])
            elif function_name == "calculate_square_area":
                result = calculate_square_area(arguments["side"])

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        print(final_response.choices[0].message.content)
    else:
        print(message.content)

if __name__ == "__main__":
    run_agent()
