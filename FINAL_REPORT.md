## Capstone Project Part 6 – Final Technical Report

### 1) Architecture Overview

- **Entry points**: `run_assistant.py` (launcher), `app/main.py` (CLI main) → `app/controller.py`.
- **Controller**: Routes user text to agents via intent detection from `app/utils/text.py`. Maintains short-term context with `LimitedMemory` in `app/memory.py`.
  - Intents: `rag|chat`, `t2i`, `sql`, `weather`, `recommender`.
  - Returns `TurnResponse` from `app/schemas.py` (text, citations, image_path, metrics).
- **RAG**: `app/rag/retriever.py` (FAISS/embeddings or basic retrieval wrapper) + `app/rag/qa.py` (answer composition with citations). Sources from `data/docs/`.
- **T2I**: `app/t2i/image_gen.py` uses Replicate when key provided; otherwise draws a recognizable stub image via Pillow. Outputs to `outputs/images/`.
- **SQL Agent**: `app/agents/sql_agent.py` uses SQLite `data/demo.db`, seeds demo tables on startup, and supports read-only `SELECT` queries.
- **Weather Agent**: `app/agents/weather_agent.py` stubbed provider returning deterministic values.
- **Recommender Agent**: `app/agents/recommender_agent.py` TF‑IDF + cosine similarity over title+description with n‑grams, synonym expansion, and rationale.
- **Configuration**: `app/utils/config.py` centralizes settings; loads from env and optional `app/utils/secrets.py`. Web search removed per requirement.
- **Logging**: `app/utils/logging.py` (optional helpers); code logs minimally to keep CLI responsive.


### 2) Key Implementation Decisions

- **Controller-first integration**: All capabilities exposed through `Controller.handle()` to ensure a single orchestration surface, no manual toggling.
- **SQLite over DuckDB**: Migrated to SQLite for easier inspection and wider tool compatibility. Explicit commits and deterministic seeding.
- **OpenAI SDK v1 compatibility**: Config ensures `OPENAI_API_KEY` is present in environment for LangChain/OpenAI usage; models configurable.
- **RAG via LangChain-compatible structure**: Retriever and QA kept modular to allow drop‑in switch between basic keyword and FAISS/embeddings.
- **T2I graceful degradation**: If Replicate fails or no key, generate meaningful stub images (cat/dog/sunset) to keep UX coherent in demos.
- **No Web Search**: Removed web fallback to keep runtime consistent and avoid external variability, per project decision.
- **Security & Config**: `app/utils/secrets.py` is optional and not committed; env overrides supported for deployment.


### 3) Debugging and Testing Process

- **PowerShell and CLI**: Standardized commands (`python -m app.main`) and avoided shell‑specific chaining. Added path fix in `app/main.py` to run from IDE.
- **Imports & Versions**: Resolved `OpenAI` import mismatches; pinned usage to SDK v1 style in configuration and LangChain adapters.
- **DB Lock & Format**: Killed stray Python processes, migrated to SQLite, and ensured tables are dropped and recreated deterministically in `seed_demo()`.
- **Image Generation**: Handled Replicate exceptions, added structured handling for non‑string outputs, and robust URL/file output writing.
- **Intent Detection**: Prioritized SQL (“select…”) before generic intents to route correctly.
- **Cleanup**: Removed web search module and keys; deleted temporary helper scripts.


### 4) How to Run (End‑to‑End Demo)

1. (Optional) Create and activate a virtual environment.
2. Set keys if available (skip if running fully offline):
   - `OPENAI_API_KEY` (RAG embeddings/LLM when configured)
   - `T2I_API_KEY` for Replicate (optional; otherwise stub images)
3. Launch:
   - `python run_assistant.py`  or  `python -m app.main`
4. Try these in order:
   - RAG: "What is artificial intelligence?"
   - Recommender: "recommend headphones"
   - SQL: `SELECT * FROM employees` (read‑only)
   - T2I: "draw a cat" (saves to `outputs/images/`)


### 5) Test Coverage (See TEST_PLAN.md)

- Smoke: imports, controller routing, basic prompt/response loop.
- RAG: retrieval non‑empty, citations emitted.
- SQL: valid SELECTs return rows; invalid SQL yields clear error.
- T2I: file created successfully with or without API key.
- Recommender: returns non‑zero scores with rationale.


### 6) Challenges and Resolutions

- Package/API drift (OpenAI v0.28 → v1): centralized config and ensured env propagation.
- Database portability and locks: switch to SQLite, explicit commits, deterministic seeding and file path handling.
- External API flakiness (Replicate/Web): robust error paths and removing web fallback to stabilize demo.
- Intent collisions: early SQL detection prevents misrouting to RAG.


### 7) Limitations & Future Work

- RAG currently uses a lightweight pipeline; could enable full LangChain conversational memory and FAISS indexing by default.
- Recommender relies on TF‑IDF; learn‑to‑rank or LLM‑reranking could further improve quality.
- Weather is a stub; swap to a real provider with caching and rate‑limit handling.
- Add structured telemetry and richer logging for production diagnostics.


### 8) Submission Checklist Mapping

- Conversational interface with limited memory: `Controller` + `LimitedMemory` ✔
- RAG QA from local docs: `retriever.py` + `qa.py`, docs in `data/docs/` ✔
- Text‑to‑image with prompt engineering: `t2i/image_gen.py` with graceful stub ✔
- Multi‑agent via controller: Weather, SQL, Recommender routed by intent ✔
- No manual switching: Single `Controller.handle()` flow ✔
- APIs/libraries documented herein and in code comments ✔


