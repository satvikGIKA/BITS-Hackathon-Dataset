# Bid Intelligence v1

Extract → SQLite → LLM SQL pipeline for the BITS hackathon corpus.

## Prerequisites

- Python 3.11+
- [OpenRouter](https://openrouter.ai/) API key in `.env`:

```bash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free   # optional, this is the default
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Build knowledge base

Extracts works and personnel certs from `documents/` into SQLite (no LLM):

```bash
python -m bidintel build-kb --documents documents --out data/kb.sqlite
```

Expected validation output: 155 works, 48 personnel certs, ~5530.4 Cr total.

## Answer sample questions

One OpenRouter call per question (one-shot SQL, no repair):

```bash
python -m bidintel answer-all \
  --db data/kb.sqlite \
  --questions sample_questions.json \
  --out my_answers.jsonl \
  -v
```

Single question:

```bash
python -m bidintel answer \
  --db data/kb.sqlite \
  --question "How many works for Jal Nigam, Jharkhand have no reference letter on file?"
```

## Score

```bash
python evaluate.py --submission my_answers.jsonl --per-question
```

## Environment

| Variable | Default |
|----------|---------|
| `OPENROUTER_API_KEY` | *(required)* |
| `OPENROUTER_MODEL` | `openrouter/free` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |

## Known limitations (v1)

- ~41 works have `grade IS NULL` (short completion certificate template).
- One-shot SQL from the LLM may fail on complex multi-hop questions.
- Financials, bonds, BOQ, ledgers not extracted.
