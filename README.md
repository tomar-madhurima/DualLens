# DualLens

A two-mode AI chatbot: **Coach**, a compassionate but honest mentor, and
**Challenger**, a critical but fair critic. Both modes work from the same
underlying idea — most people don't fully know what to ask, so the goal
isn't just answering the literal question, but understanding what the
person actually needs and responding accordingly.

- **Coach** teaches, fills in gaps the user didn't think to ask about, and
  is encouraging without ever sugarcoating.
- **Challenger** stress-tests ideas, questions assumptions, and only
  offers praise when there's real evidence behind it.

## How it works

```
User message
    -> pick system prompt (Coach or Challenger)
    -> send prompt + conversation history to Gemini
    -> show response
    -> persist conversation history to Supabase (Postgres)
```

No multi-agent pipeline or reasoning "engine" — one function calls Gemini,
one module handles persistence. The behavior comes from well-designed
system prompts, not architectural complexity.

## Tech stack

- **Python** + **Streamlit** for the UI
- **Google Gemini API** for the model
- **Supabase (Postgres)** for persisting conversation history
- **Firebase Firestore** and **Claude/GPT** were also considered — reasoning
  in the repo's commit history / dev notes if curious

## Status

Early prototype (v1). Currently: two modes, one model backend, persistent
storage per mode. Not yet: per-user accounts, multi-model support, or a
custom frontend beyond Streamlit.

## Files

- `app.py` — the Streamlit app (UI + Gemini API calls)
- `prompts.py` — the Coach and Challenger system prompts
- `storage.py` — Supabase load/save/clear functions
- `requirements.txt` — Python dependencies
