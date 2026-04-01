from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EffectContext:
    source: Any
    targets: list[Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    spent_amount: int = 0
    chosen_stat: str | None = None

    def with_targets(self, targets) -> "EffectContext":
        return type(self)(
            source=self.source,
            targets=list(targets),
            metadata=dict(self.metadata),
            spent_amount=self.spent_amount,
            chosen_stat=self.chosen_stat,
        )

@dataclass(slots=True)
class Effect:
    def apply(self, context: EffectContext):
        raise NotImplementedError
    
