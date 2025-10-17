from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Turn:
    user_text: str

@dataclass
class TurnResponse:
    response_text: str
    citations: List[str] = field(default_factory=list)
    image_path: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
