# Bid Intelligence v2 — Shape Router

Extract → SQLite → **shape-routed SQL templates** (primary) with LLM SQL fallback.

## Prerequisites

- Python 3.11+
- [OpenRouter](https://openrouter.ai/) API key in `.env` (only needed for LLM fallback)

```bash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free   # optional
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

**Template-only (recommended for samples — no API calls):**

```bash
python -m bidintel answer-all \
  --db data/kb.sqlite \
  --questions sample_questions.json \
  --out my_answers.jsonl \
  --no-llm-fallback \
  -v
```

**With LLM fallback** for unknown shapes:

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
  --question "How many works for Jal Nigam, Jharkhand have no reference letter on file?" \
  --no-llm-fallback
```

## Score

```bash
python evaluate.py --submission my_answers.jsonl --per-question
```

Target on samples: **25.0 / 25**.

## Architecture

1. **Classify** question into one of 13 shapes (`bidintel/classify.py`)
2. **Extract slots** from question text using DB allowlists (`bidintel/slots.py`)
3. **Render SQL** from shape templates (`bidintel/shapes.py`)
4. **Fallback** to LLM one-shot SQL if shape/slots fail (`bidintel/answer.py`)

## Tests

```bash
pytest tests/ -v
```

Includes shape classification, grade extraction, and end-to-end template scoring against all 25 sample questions.

## Environment

| Variable | Default |
|----------|---------|
| `OPENROUTER_API_KEY` | *(required for LLM fallback)* |
| `OPENROUTER_MODEL` | `openrouter/free` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |

## KB improvements (v2)

- **Grades:** short CCs use `satisfactory completion of the final inspection` as formal `Satisfactory`; `found satisfactory during the final inspection` is not a grade
- **Money:** prefer precise CC Indian-comma values over crore-rounded CCC values when they differ

## Known limitations

- Financials, bonds, BOQ, ledgers, CVs not extracted (Approach C)
- Shape router covers the 13 sample shapes; hidden-set shapes may need new templates or LLM fallback
