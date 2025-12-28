---
title: Career_Conversation
app_file: app.py
sdk: gradio
live running app: https://huggingface.co/spaces/Reda-b/Career_Conversation
---


# Personal Website AI Chat Assistant
**Author:** Reda Baddy  
**Goal:** Provide an AI-powered assistant for interacting with visitors on a personal website.

---

## Overview
This project implements an AI chat assistant that represents **Reda Baddy** on his personal website. The assistant can:

- Answer questions about Reda's career, background, skills, and experience.
- Record visitor emails and notes for future contact.
- Log any unknown questions automatically for further follow-up.

It leverages **OpenAI**, **Groq**, and **Gradio** to provide an interactive chat experience.

---

## Features
1. **Context-Aware Responses:**  
   The assistant uses a combination of a summary and a resume to answer questions accurately.

2. **Tool Integration:**  
   - `record_user_details`: Logs user emails, names, and notes.  
   - `record_unknown_question`: Logs questions that the assistant cannot answer.  

3. **Interactive Chat Interface:**  
   Built with **Gradio** for a clean web interface.

4. **Notifications:**  
   Uses **Pushover** to send notifications whenever a user or unknown question is recorded.

---

## Environment Setup
1. Clone the repository.  
2. Install dependencies:

```bash
pip install openai groq gradio requests python-dotenv
```
3. Create a .env file with your credentials:
PUSHOVER_TOKEN=<your_pushover_token>
PUSHOVER_USER=<your_pushover_user_key>
OPENAI_API_KEY=<your_openai_key>

## Usage

1. Prepare your context files:
cv.md → Your full resume in markdown format.
summary.txt → Short summary of your professional or personnal background.

2. Run the application:
python app.py
Open the Gradio interface in your browser.
