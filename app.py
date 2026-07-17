"""
DualLens v1 - a two-mode chatbot (Coach / Challenger) running on Gemini,
with conversation history persisted to Supabase (Postgres).

Run with:
    streamlit run app.py

Requires environment variables:
    GEMINI_API_KEY            (get one free at https://aistudio.google.com/apikey)
    SUPABASE_URL, SUPABASE_KEY (your Supabase project URL and service_role key)
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv
from prompts import COACH_PROMPT, CHALLENGER_PROMPT
import storage

load_dotenv()  # loads GEMINI_API_KEY / SUPABASE_URL / SUPABASE_KEY from a local .env file

from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

GEMINI_MODEL = "gemini-3.5-flash"  # fast + free-tier friendly; swap to a pro model later if needed
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Core response function - this is the entire "engine". One function,
# two prompt variants, one backend (Gemini) for now.
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

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            )
            return response.text
        except ServerError:
            # 503 UNAVAILABLE / model overloaded - common on the free tier.
            # Wait a bit and retry a couple of times before giving up.
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 * (attempt + 1))  # 2s, then 4s
                continue
            return (
                "⚠️ Gemini is experiencing high demand right now (this is common "
                "on the free tier, not a bug in the app). Please try again in a "
                "moment."
            )
        except ClientError as e:
            return f"⚠️ Gemini rejected the request: {e}"


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="DualLens")
st.title("DualLens")
st.caption("Coach: compassionate but honest.  Challenger: critical but fair.  (Gemini + Supabase)")

# Load history from Supabase once per session, per mode (not re-fetched on every rerun).
if "history" not in st.session_state:
    st.session_state.history = {}

mode = st.radio("Mode", ["Coach", "Challenger"], horizontal=True)

if mode not in st.session_state.history:
    try:
        st.session_state.history[mode] = storage.load_history(mode)
    except Exception as e:
        st.error(f"Couldn't load saved conversation from Supabase: {e}")
        st.session_state.history[mode] = []

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

    try:
        storage.save_history(mode, st.session_state.history[mode])
    except Exception as e:
        st.warning(f"Response shown, but couldn't save to Supabase: {e}")

with st.sidebar:
    st.subheader("About")
    st.write(
        "DualLens v1 — a minimal two-mode chatbot. Each mode is just a "
        "different system prompt sent to the same model. Conversation "
        "history is persisted to Supabase, so it survives "
        "closing and reopening the app."
    )
    if st.button("Clear this mode's conversation"):
        st.session_state.history[mode] = []
        try:
            storage.clear_history(mode)
        except Exception as e:
            st.warning(f"Cleared locally, but couldn't clear Supabase: {e}")
        st.rerun()
