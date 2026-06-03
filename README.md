# AgriPride AI

A simple agricultural assistant built as a multi-agent Python project with Gemini API integration.

## Setup

1. Copy the example environment file:

```bash
copy .env.example .env
```

2. Add your Gemini API key to `.env`:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-pro
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run locally

```bash
python main.py
```

## Run the Streamlit UI

```bash
streamlit run streamlit_app.py
```

## Project structure

- `main.py` — entry point for CLI execution
- `crew.py` — orchestrates agents and workflow
- `gemini_client.py` — Gemini API wrapper
- `agents/` — agent implementations
- `tools/` — market, weather, and logistics helpers
- `memory/` — shared memory storage
- `workflows/` — validation and escalation logic
- `streamlit_app.py` — web UI interface
