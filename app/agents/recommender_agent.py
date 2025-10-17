
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import unicodedata
from typing import List, Dict

try:
    # Optional: allow lightweight LLM re-ranking/enrichment
    import openai
    from app.utils.config import settings
    _HAS_OPENAI = bool(getattr(settings, "OPENAI_API_KEY", ""))
    _ONLINE = bool(getattr(settings, "RECOMMENDER_ONLINE_ENRICHMENT", False))
    if _HAS_OPENAI:
        openai.api_key = settings.OPENAI_API_KEY
except Exception:
    _HAS_OPENAI = False
    _ONLINE = False

class RecommenderAgent:
    def __init__(self):
        self.items = [
            {"id": 1, "title": "Noise-cancelling headphones", "desc": "over-ear bluetooth travel ANC wireless"},
            {"id": 2, "title": "Running shoes", "desc": "lightweight breathable daily trainer cushioned"},
            {"id": 3, "title": "Mechanical keyboard", "desc": "tactile switches compact rgb quiet office"},
        ]

        # Build a richer text field combining title + description for better recall
        corpus: List[str] = [
            f"{it['title']} {it['desc']}" for it in self.items
        ]

        # Stronger TF-IDF: unigrams+bigrams, english stopwords, lowercase, simple normalization
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            lowercase=True,
            min_df=1,
        )
        self.mat = self.vectorizer.fit_transform([self._normalize_text(c) for c in corpus])

        # Domain synonyms/expansions to bridge vocabulary gaps
        self.synonyms: Dict[str, List[str]] = {
            "headphone": ["headphones", "over-ear", "anc", "noise cancelling", "bluetooth", "wireless"],
            "headphones": ["headphone", "over-ear", "anc", "noise cancelling", "bluetooth", "wireless"],
            "earphone": ["earbuds", "in-ear"],
            "shoes": ["running", "trainer", "sneakers", "breathable", "lightweight"],
            "keyboard": ["mechanical", "tactile", "compact", "rgb", "quiet"],
        }

    def _normalize_text(self, text: str) -> str:
        t = unicodedata.normalize("NFKC", text)
        t = t.lower()
        t = re.sub(r"[^a-z0-9\s]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _expand_query(self, query: str) -> str:
        q = self._normalize_text(query)
        tokens = q.split()
        expanded: List[str] = []
        for tok in tokens:
            expanded.append(tok)
            if tok in self.synonyms:
                expanded.extend(self.synonyms[tok])
        return " ".join(expanded)

    def run(self, query: str, k: int = 2):
        # Expand and normalize the query for better lexical overlap
        expanded_query = self._expand_query(query)
        qv = self.vectorizer.transform([expanded_query])
        sims = cosine_similarity(qv, self.mat)[0]
        idxs = np.argsort(-sims)[:k]
        results = []
        for i in idxs:
            item = dict(self.items[int(i)])
            score = float(sims[int(i)])
            # Short rationale: show top overlapping features from vector vocab
            rationale = None
            try:
                vocab = self.vectorizer.get_feature_names_out()
                qnz = qv.toarray()[0]
                inz = self.mat[int(i)].toarray()[0]
                contrib = (qnz * inz)
                top_idx = np.argsort(-contrib)[:3]
                feats = [vocab[j] for j in top_idx if contrib[j] > 0]
                if feats:
                    rationale = ", ".join(feats)
            except Exception:
                rationale = None
            item.update({"score": score})
            if rationale:
                item["why"] = rationale
            results.append(item)

        # Optional re-ranking using LLM for tie-breaking/semantic boost
        if _HAS_OPENAI and _ONLINE:
            try:
                prompt = (
                    "Given the user query and a list of items (title + desc), "
                    "return the best top items in order. Only re-rank; do not invent new items.\n"
                    f"Query: {query}\n\n"
                    f"Items:\n" +
                    "\n".join([f"- {r['title']}: {r['desc']}" for r in results]) +
                    "\n\nRespond with the reordered list of titles separated by newlines."
                )
                resp = openai.ChatCompletion.create(
                    model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": "You are a ranking assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                )
                order = [t.strip("- ") for t in resp.choices[0].message.content.splitlines() if t.strip()]
                title_to_item = {it["title"]: it for it in results}
                reranked = [title_to_item[t] for t in order if t in title_to_item]
                # Preserve any items not mentioned by LLM at the end
                tail = [it for it in results if it not in reranked]
                results = reranked + tail
            except Exception:
                pass

        # Optional brand/link enrichment as a final step
        if _HAS_OPENAI and _ONLINE:
            try:
                enrich_prompt = (
                    "For each item below, suggest 1-2 reputable brand models and a short reason. "
                    "Output one line per item as: Title — Brands: <brand1, brand2> — Note: <why>. "
                    f"\nQuery: {query}\nItems:\n" +
                    "\n".join([r['title'] for r in results])
                )
                resp = openai.ChatCompletion.create(
                    model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": "You enrich recommendations with concrete brands."},
                        {"role": "user", "content": enrich_prompt},
                    ],
                    temperature=0.2,
                )
                lines = [ln for ln in resp.choices[0].message.content.splitlines() if ln.strip()]
                for i, ln in enumerate(lines[:len(results)]):
                    results[i]["why"] = results[i].get("why") or ln.strip()
            except Exception:
                pass

        return results
