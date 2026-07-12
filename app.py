"""
DualMind v1 - a two-mode chatbot (Coach / Challenger) running on Gemini.

Run with:
    streamlit run app.py

Requires an environment variable:
    GEMINI_API_KEY
(Get one free at https://aistudio.google.com/apikey)
"""

import os
import streamlit as st
from dotenv import load_dotenv
from prompts import COACH_PROMPT, CHALLENGER_PROMPT

load_dotenv()  # loads GEMINI_API_KEY from a local .env file, if present

from google import genai
from google.genai import types

GEMINI_MODEL = "gemini-3.5-flash"  # fast + free-tier friendly; swap to a pro model later if needed


# ---------------------------------------------------------------------------
# Core response function - this is the entire "engine". One function,
# two prompt variants, one backend (Gemini).
# ---------------------------------------------------------------------------
def get_response(user_message: str, mode: str, history: list) -> str:
    system_prompt = COACH_PROMPT if mode == "Coach" else CHALLENGER_PROMPT
    return call_gemini(system_prompt, history, user_message)


def call_gemini(system_prompt: str, history: list, user_message: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ GEMINI_API_KEY is not set. Add it to your .env file to use Gemini."

    client = genai.Client(api_key=api_key)

    # Gemini's "contents" list uses role "user"/"model" (not "assistant")
    contents = []
    for turn in history:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=turn["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    return response.text


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="DualMind", page_icon="🧠")
st.title("🧠 DualMind")
st.caption("Coach: compassionate but honest.  Challenger: critical but fair.  (Running on Gemini)")

# Separate conversation history per mode (v1 keeps them independent).
if "history" not in st.session_state:
    st.session_state.history = {"Coach": [], "Challenger": []}

mode = st.radio("Mode", ["Coach", "Challenger"], horizontal=True)

# Show the conversation history for the currently selected mode
for turn in st.session_state.history[mode]:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])

user_message = st.chat_input("What's on your mind?")

if user_message:
    with st.chat_message("user"):
        st.write(user_message)

    with st.chat_message("assistant"):
        with st.spinner(f"{mode} is thinking..."):
            reply = get_response(user_message, mode, st.session_state.history[mode])
        st.write(reply)

    st.session_state.history[mode].append({"role": "user", "content": user_message})
    st.session_state.history[mode].append({"role": "assistant", "content": reply})

with st.sidebar:
    st.subheader("About")
    st.write(
        "DualMind v1 — a minimal two-mode chatbot. Each mode is just a "
        "different system prompt sent to the same model. No multi-agent "
        "pipeline, no separate reasoning stages — the persona and "
        "reasoning behavior all live in the prompt."
    )
    if st.button("Clear this mode's conversation"):
        st.session_state.history[mode] = []
        st.rerun()
