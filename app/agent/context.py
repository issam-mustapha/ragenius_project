from dataclasses import dataclass
from typing import Optional
@dataclass
class Context:
    user_id: int
    image_text: Optional[str] = None