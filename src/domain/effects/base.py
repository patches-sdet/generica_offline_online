from dataclasses import dataclass
from typing import List, Any


@dataclass
class EffectContext:
    source: Any
    targets: List[Any]
    metadata: dict = None

@dataclass
class Effect:
    def apply(self, context: EffectContext):
        raise NotImplementedError
