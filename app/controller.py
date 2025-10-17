
from .memory import LimitedMemory
from .utils.text import detect_intent, normalize
from .schemas import Turn, TurnResponse
from .rag.retriever import Retriever
from .rag.qa import compose_answer
from .t2i.image_gen import ImageGenerator
from .agents.weather_agent import WeatherAgent
from .agents.sql_agent import SQLAgent
from .agents.recommender_agent import RecommenderAgent
from .utils.config import settings

class Controller:
    def __init__(self):
        self.mem = LimitedMemory(max_turns=6)
        self._retriever=None; self._img=ImageGenerator()
        self._weather=WeatherAgent(); self._sql=SQLAgent(); self._sql.seed_demo()
        self._rec=RecommenderAgent()

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = Retriever("indices/vector", "sentence-transformers/all-MiniLM-L6-v2")
        return self._retriever

    def handle(self, turn: Turn) -> TurnResponse:
        text = normalize(turn.user_text)
        intent = detect_intent(text)

        if intent == "t2i":
            prompt=self._img.build_prompt(subject=text)
            path=self._img.generate(prompt)
            reply=f"🖼️ Generated image saved to: {path}"
            self.mem.add(text,reply)
            return TurnResponse(response_text=reply,image_path=path)

        if intent in {"rag","chat"}:
            ans,cits=compose_answer(text,self.retriever)
            reply=ans+(f"\n📚 Sources: {', '.join(set(cits))}" if cits else "")
            # Web fallback removed per request
            self.mem.add(text,reply)
            return TurnResponse(response_text=reply,citations=cits)

        if intent=="weather":
            d=self._weather.run(location=text)
            reply=f"🌤️ {d['location']}: {d['temp_c']}°C, {d['summary']} (humidity {d['humidity']})"
            self.mem.add(text,reply)
            return TurnResponse(response_text=reply,metrics=d)

        if intent=="sql":
            if not text.lower().startswith("select"):
                return TurnResponse(response_text="⚠️ Only SELECT queries allowed.")
            try:
                rows=self._sql.run(text)
                reply=f"📊 Rows: {rows[:3]}... (total {len(rows)})"
            except Exception as e:
                reply=f"SQL error: {e}"
            self.mem.add(text,reply)
            return TurnResponse(response_text=reply)

        if intent=="recommender":
            recs=self._rec.run(text)
            def _fmt(r):
                why = f" — {r['why']}" if isinstance(r, dict) and r.get('why') else ""
                return f"- {r['title']} (score {r['score']:.2f}){why}"
            lines=["🛍️ Recommended items:"]+[_fmt(r) for r in recs]
            reply="\n".join(lines)
            self.mem.add(text,reply)
            return TurnResponse(response_text=reply)

        fb="🤖 Ask about documents, images, weather, SQL, or recommendations."
        self.mem.add(text,fb)
        return TurnResponse(response_text=fb)
