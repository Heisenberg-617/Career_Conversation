from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
import json
import os
import requests
import gradio as gr


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]

def normalize_history(history):
    clean = []
    for h in history:
        if isinstance(h, dict):
            # Keep only role + content (drop metadata)
            clean.append({
                "role": h.get("role"),
                "content": h.get("content", "")
            })
        elif isinstance(h, (list, tuple)) and len(h) == 2:
            # Older Gradio formats
            clean.append({"role": "user", "content": h[0]})
            clean.append({"role": "assistant", "content": h[1]})
    return clean

class Me:

    def __init__(self):
        self.openai = OpenAI()
        self.groq = Groq()
        self.name = "Reda Baddy"

        with open("me/cv.md", "r", encoding="utf-8") as f:
            self.resume = f.read()
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and resume  which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## Resume:\n{self.resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        history_clean = normalize_history(history)
    
        messages = [{"role": "system", "content": self.system_prompt()}]
        messages.extend(history_clean)
        messages.append({"role": "user", "content": message})
    
        done = False
        final_response = ""
        
        while not done:
            response = self.groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        
            choice = response.choices[0]
            msg = choice.message
        
            # TOOL CALL?
            if choice.finish_reason == "tool_calls":
                tool_calls = msg.tool_calls
        
                # Add assistant call message (even if empty)
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [tc.model_dump() for tc in tool_calls]
                })
        
                # Execute tools
                results = self.handle_tool_call(tool_calls)
        
                # Return tool results back to the model
                for r in results:
                    messages.append(r)
        
            else:
                # FINAL MESSAGE
                final_response = msg.content or ""
                done = True
        
        return final_response



if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()
