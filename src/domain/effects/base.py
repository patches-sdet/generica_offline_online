from dataclasses import dataclass, field
from typing import Any


class CONTEXT_OPTIONS:
    TIER = "tier"
    PRODUCT_TYPE = "product_type"
    CHOSEN_ITEM = "chosen_item"
    CHOSEN_JOB = "chosen_job"
    BLESSING_STAT = "blessing_stat"
    DEITY = "deity"
    SUMMON_TYPE = "summon_type"
    INSPECTION_MODE = "inspection_mode"

def get_context_option(ctx: "EffectContext", key: str, default=None):
    return ctx.metadata.get(key, default)


def require_context_option(ctx: "EffectContext", key: str):
    if key not in ctx.metadata:
        raise ValueError(f"Missing required context option: {key}")
    return ctx.metadata[key]

@dataclass(slots=True)
class EffectContext:
    source: Any
    targets: list[Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    # common reusable activation inputs
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

    def get_option(self, key: str, default=None):
        return self.metadata.get(key, default)

    def require_option(self, key: str):
        if key not in self.metadata:
            raise ValueError(f"Missing required context option: {key}")
        return self.metadata[key]

@dataclass(slots=True)
class Effect:
    def apply(self, context: EffectContext):
        raise NotImplementedError