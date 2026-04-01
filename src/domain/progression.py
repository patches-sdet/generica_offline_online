from dataclasses import dataclass

@dataclass
class Progression:
    name: str
    type: str  # "adventure" | "profession" | "race" | "advanced"
    level: int = 1

    def get_progression_level(self, name: str, type: str) -> int:
        p = self.progressions.get((type, name))
        return p.level if p else 0