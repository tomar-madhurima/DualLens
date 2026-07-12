# DualMind (v1 - Gemini)

A minimal two-mode chatbot: **Coach** (compassionate but honest mentor) and
**Challenger** (critical but fair critic). Running on Google's Gemini API
for now.

## How it works

There's no multi-agent pipeline or reasoning "engine." Each mode is just a
different system prompt (see `prompts.py`) sent to Gemini. One function
(`get_response`) handles both modes.

```
User message
    -> pick system prompt (Coach or Challenger)
    -> send system prompt + conversation history + message to Gemini
    -> show response
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get a Gemini API key (free tier available, no credit card required):
   - Go to https://aistudio.google.com/apikey
   - Sign in with a Google account, click "Create API key"

3. Set your key:
   - Copy `.env.example` to a new file named `.env`
   - Fill in your real key in `.env`:
     ```
     GEMINI_API_KEY=your-real-key-here
     ```
   - `.env` is already listed in `.gitignore`, so it will never be committed
     to GitHub — only `.env.example` (with placeholder text) is meant to be
     committed.

   **Never** paste a real key directly into `app.py`, `prompts.py`, or any
   file you plan to commit.

4. Run the app:
   ```
   streamlit run app.py
   ```
   This opens a browser tab with the chat interface.

## Before you push to GitHub

Double check `.env` is NOT tracked by git:
```
git status
```
`.env` should not appear in the list of files to be committed. If you
already committed a real key by accident at some point, changing the file
afterward is not enough — the key is still visible in git history. In that
case, revoke/rotate that key from https://aistudio.google.com/apikey and
generate a new one.

## What's in v1

- Mode toggle: Coach / Challenger
- Gemini as the backend model
- Separate conversation history per mode
- Simple chat UI (Streamlit's built-in chat components)

## What's intentionally NOT in v1 (future ideas)

- Claude / GPT as alternate or additional backends (the code is structured
  so this is a small addition later, not a rewrite)
- "Both modes at once" responses
- Memory across sessions (currently resets when you close the app)
- Mental Model / Unknown-Unknown detection as a distinct reasoning stage
- Multi-agent orchestration
- A proper frontend (React, etc.) instead of Streamlit

Get v1 working and tested first. Add complexity only once you've felt where
the simple version actually falls short.

## Files

- `app.py` — the Streamlit app (UI + Gemini API calls)
- `prompts.py` — the Coach and Challenger system prompts
- `requirements.txt` — Python dependencies
- `.env.example` — template for your API key (copy to `.env`, fill in the real value — `.env` is gitignored)
- `.gitignore` — makes sure `.env` and other local-only files never get committed
