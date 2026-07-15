# Design Decisions

Short log of the main tradeoffs considered while building DualLens, and why
each choice was made. Kept separate from `README.md` so the main overview
stays brief.

## Model backend: Gemini (over Claude / GPT)

Considered running Coach and Challenger through different model providers
(e.g. Claude for one, GPT for the other) to get distinct "voices" out of the
box. Started with a single provider instead for v1 — simpler to build and
test, and it isolates whether the two-mode concept itself works before
adding multi-provider complexity. Gemini specifically for its generous free
tier, which makes iterating cheap. The code is structured so a second
provider (Claude or GPT) is a small addition later, not a rewrite — the
persona logic lives entirely in system prompts, not in provider-specific code.

## Storage: Supabase (over Firebase Firestore)

Considered Firebase Firestore first (NoSQL, generous free Spark plan,
minimal setup). Switched to Supabase because:
- It's real Postgres — SQL experience is more broadly asked for in job
  postings than Firestore-specific NoSQL experience.
- No daily read/write quota (Firestore's free tier caps at 50K reads / 20K
  writes per day; unlikely to hit this as a solo project, but Supabase's
  model is simpler to reason about).
- Trade-off: free Supabase projects pause after 7 days of inactivity
  (a minor annoyance, not a functional problem — the project just wakes up
  slower on the next request).

## UI: Streamlit (over a custom frontend)

Streamlit gives a working chat UI in a few dozen lines of Python, with no
separate frontend build step. This keeps v1 focused on testing whether the
Coach/Challenger persona design actually works, rather than on frontend
polish. A custom frontend (e.g. React) is a reasonable v2 addition once the
core concept is validated.

## Two separate conversation histories (per mode, not per model)

Coach and Challenger keep independent conversation threads rather than
sharing one history. This was simpler to implement, and arguably more
honest — the two personas genuinely have different "memory" of what
matters in a conversation.
