# Week 13 AI Assistant – Manual Test Plan

Purpose: A concise checklist you can execute in sequence to verify all features work after setup or changes.

Prereqs
- Python 3.10+
- In `app/utils/config.py` set valid keys if available:
  - `OPENAI_API_KEY` (required for LangChain RAG + LLM features)
  - `T2I_API_KEY` (optional; Replicate image gen falls back to stub if missing)
- Optional toggles:
  - `RECOMMENDER_ONLINE_ENRICHMENT` = False (offline) or True (adds brand notes using OpenAI)

Run Command
```
python run_assistant.py
```

Legend
- Input → what to type at `🧑 You:`
- Expect → key behavior to observe (not literal match)

---

## 1) Conversational Interface + Memory
1. Input: `hello`
   - Expect: Friendly greeting.
2. Input: `what can you do?`
   - Expect: Lists features (RAG, images, weather, SQL, recommendations).
3. Input: `and remind me what you just said`
   - Expect: Response reflects previous turns (limited memory active).

## 2) Multi‑Agent Routing (Controller)
1. Input: `draw a cat`
   - Expect: Image path printed; file appears in `outputs/images/`.
2. Input: `weather in singapore`
   - Expect: Weather agent reply (stub values unless configured).
3. Input: `SELECT * FROM employees`
   - Expect: SQL agent returns rows count and sample rows.
4. Input: `recommend headphones`
   - Expect: Recommender returns ranked items with non‑zero score and a short rationale.

## 3) RAG – Document Q&A (LangChain + FAISS)
Setup: Ensure `.txt` docs exist in `data/docs/` (already provided: `ai_basics.txt`, `programming_tips.txt`, `generative_ai_overview.txt`).
1. Input: `What is artificial intelligence?`
   - Expect: Grounded answer; `📚 Sources:` list includes a doc filename.
2. Input: `List two common applications of AI`
   - Expect: Applications from docs; citations printed.
3. Input: `According to the documents, what is RAG?`
   - Expect: RAG definition; citations include `example_doc.txt` (if content present).
4. Input: `The previous answer—can you summarize it in one line?`
   - Expect: One‑line summary that stays consistent with prior context.

## 4) Text‑to‑Image (T2I)
1. Input: `draw a futuristic city at sunset`
   - Expect: 
     - If `T2I_API_KEY` valid: image downloaded; no error logs.
     - If missing/invalid: stub image generated with descriptive overlay; still saves a PNG.
2. (Optional quality) Input: `draw a product photo of a coffee mug, studio lighting`
   - Expect: Output image saved; no crash.

## 5) SQL Agent (SQLite)
1. Input: `SELECT * FROM sales`
   - Expect: 6 rows total; sample rows printed.
2. Input: `SELECT department, AVG(salary) FROM employees GROUP BY department`
   - Expect: Averages per department printed (IT, Marketing, Sales).
3. Input: `SELECT * FROM products WHERE category='Electronics'`
   - Expect: At least laptop/mouse/monitor.
4. Input: `UPDATE employees SET salary=0` (negative test)
   - Expect: `⚠️ Only SELECT queries allowed.`

## 6) Recommender Agent
Base (offline) TF‑IDF + synonyms:
1. Input: `recommend headphones`
   - Expect: Non‑zero score for headphones; rationale tokens (e.g., `anc, bluetooth`).
2. Input: `suggest breathable daily trainer`
   - Expect: Running shoes at the top with non‑zero score.
3. Input: `recommend quiet office keyboard`
   - Expect: Mechanical keyboard with non‑zero score.

Online enrichment (optional):
- Set `RECOMMENDER_ONLINE_ENRICHMENT=True` and provide `OPENAI_API_KEY`.
- Repeat the three queries above.
  - Expect: Same ranking plus a short brand/why note appended.

## 7) Error Handling & Fallbacks
1. Temporarily clear `OPENAI_API_KEY` and run `What is artificial intelligence?`
   - Expect: A graceful error message (no crash) or minimal response from fallback path.
2. Temporarily clear `T2I_API_KEY` and run `draw a cat`
   - Expect: Stub image saved; message indicates success with local stub.
3. Input: `select * from nonexisting`
   - Expect: `SQL error:` with explanation (no process crash).

## 8) Non‑Functional Checks
1. Quick start: `python run_assistant.py` runs without stack traces.
2. Logs/errors: No repeated noisy tracebacks on normal usage.
3. Outputs: Images saved under `outputs/images/`; no giant files checked into repo.

---

Troubleshooting Quick Reference
- If RAG returns no sources: ensure docs exist in `data/docs/` and the OpenAI key is set.
- If SQL errors about locks: close prior Python processes; the app holds a single connection.
- If image gen fails: confirm `T2I_API_KEY` or rely on stub (file still saved).


