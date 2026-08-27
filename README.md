# Axiom AI

Axiom AI is an evidence-gated government technology evaluation and procurement prototype that converts government challenges into measurable Outcome Contracts, tests solutions under a Government Pilot Twin, independently validates evidence, maps failure conditions, and provides deterministic procurement and scale-up recommendations while keeping final authorization with humans.

## Architecture

```
Problem
→ Outcome Contract
→ Government Pilot Twin
→ Private Test Matrix
→ Golden Reference Suite
→ Independent Evaluation
→ Evidence
→ Evidence Confidence
→ Failure Cartography
→ Procurement Decision
→ Vendor Response
→ Human Authorization
→ Scale-Up Review
```

## Project Structure

- `ai/` — Core governance, artifact integrity, evaluation, confidence calculation, failure cartography, scale policy, and data governance logic.
- `app/` — FastAPI prototype application providing endpoints for running demonstrations and retrieving governance summaries.
- `tests/` — Comprehensive automated governance and integration test suite (474 tests passing).

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GalaxyNova10/Axiom-AI-SIH-.git
   cd Axiom-AI-SIH-
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Environment

Copy `.env.example` to `.env` and provide the required API key if live LLM functionality is being used:
```bash
cp .env.example .env
```
*(Note: If no `OPENAI_API_KEY` is provided, the contract extraction engine automatically falls back to deterministic extraction logic. Never commit `.env` to Git.)*

## Testing

Run the full offline governance and integration test suite:
```bash
python -m pytest -v
```

The current verified baseline is:
```
474 passing tests
```

## Running the API

Start the FastAPI development server:
```bash
python -m uvicorn app.main:app --reload
```

### Available Endpoints

- `GET /health` — Service health and identity check
- `POST /api/demo/run` — Executes the complete 14-stage end-to-end governance pipeline
- `GET /api/demo/summary` — Retrieves structured governance summary for dashboard visualization
