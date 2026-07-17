"""
Persistent conversation storage using Supabase (Postgres).

This keeps storage logic separate from the UI/API code in app.py, so if you
ever swap Supabase for something else later, only this file needs to change.

Data model (kept intentionally simple for v1):
    table: "conversations"
    columns:
        mode      (text, primary key) -- "Coach" or "Challenger"
        messages  (jsonb)             -- list of {"role": ..., "content": ...} dicts

This means there's one shared conversation history per mode, not per user.
That's fine for a solo prototype; if you ever add multiple users, you'd add
a user_id column and key on (user_id, mode) instead.
"""

import os
from supabase import create_client, Client

_client: Client = None


def _get_client() -> Client:
    """Create the Supabase client once and reuse it."""
    global _client
    if _client is not None:
        return _client

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and/or SUPABASE_KEY are not set. Add them to your "
            ".env file (see README)."
        )

    _client = create_client(url, key)
    return _client


def load_history(mode: str) -> list:
    """Load saved messages for a mode. Returns [] if nothing is stored yet."""
    client = _get_client()
    result = client.table("conversations").select("messages").eq("mode", mode).execute()
    if result.data:
        return result.data[0]["messages"]
    return []


def save_history(mode: str, history: list) -> None:
    """Overwrite the stored messages for a mode with the current history."""
    client = _get_client()
    client.table("conversations").upsert({"mode": mode, "messages": history}).execute()


def clear_history(mode: str) -> None:
    """Delete the stored conversation for a mode."""
    client = _get_client()
    client.table("conversations").delete().eq("mode", mode).execute()
