from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Progression:
    name: str
    type: str   # "race" | "adventure" | "profession" | "advanced"
    level: int = 1