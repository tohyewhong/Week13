
from collections import deque
from typing import List, Tuple

class LimitedMemory:
    def __init__(self, max_turns: int = 6):
        self.buf = deque(maxlen=max_turns)

    def add(self, user: str, assistant: str):
        self.buf.append((user, assistant))

    def context(self) -> List[Tuple[str, str]]:
        return list(self.buf)

    def to_prompt(self) -> str:
        lines = []
        for i, (u, a) in enumerate(self.buf, 1):
            lines.append(f"User {i}: {u}")
            lines.append(f"Assistant {i}: {a}")
        return "\n".join(lines[-10:])
