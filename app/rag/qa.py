
from langchain_openai import ChatOpenAI
from ..utils.config import settings

def compose_answer(query: str, retriever):
    ctx = retriever.search(query, k=4)
    if not ctx:
        return "No relevant context found.", []
    context_text = "\n\n".join(
        [f"[{i+1}] {c['meta']['source']}:\n{c['text']}" for i, c in enumerate(ctx)]
    )
    citations = [c["meta"]["source"] for c in ctx]
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.3)
    system_prompt = (
        "You are a helpful assistant that answers questions using the provided context. "
        "Always cite sources like [1], [2]. If not mentioned, say so."
    )
    messages = [
        ("system", system_prompt),
        ("user", f"Question: {query}\n\nContext:\n{context_text}\n\nAnswer:"),
    ]
    try:
        ans = llm.invoke(messages).content.strip()
    except Exception as e:
        ans = f"OpenAI API error: {e}"
    return ans, citations
