from dataclasses import dataclass, field
from typing import Dict, List

from domain.effects import Effect, make_effects

# =========================
# CORE DATACLASS
# =========================

@dataclass(frozen=True)
class ProfessionJob:
    name: str

    effects_on_acquire: List[Effect] = field(default_factory=list)
    effects_per_level: List[Effect] = field(default_factory=list)

    # Future systems
    crafting_tags: List[str] = field(default_factory=list)
    gathering_tags: List[str] = field(default_factory=list)
    economic_tags: List[str] = field(default_factory=list)

    # -------------------------
    # REQUIRED FOR ENGINE
    # -------------------------

    def get_effects(self, level: int) -> List[Effect]:
        effects = []

        effects.extend(self.effects_on_acquire)

        for _ in range(level - 1):
            effects.extend(self.effects_per_level)

        return effects

    # -------------------------

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
            "crafting_tags": self.crafting_tags,
            "gathering_tags": self.gathering_tags,
            "economic_tags": self.economic_tags,
        }


# =========================
# REGISTRY
# =========================

PROFESSION_REGISTRY: Dict[str, ProfessionJob] = {}


def register_profession(job: ProfessionJob):
    PROFESSION_REGISTRY[job.name.lower()] = job


def resolve_profession(name: str) -> ProfessionJob:
    job = PROFESSION_REGISTRY.get(name.lower())
    if not job:
        raise ValueError(f"Unknown profession: {name}")
    return job


# =========================
# FACTORY
# =========================

def make_profession(
    name: str,
    stats: dict,
    crafting: List[str] = None,
    gathering: List[str] = None,
    economic: List[str] = None,
) -> ProfessionJob:

    job = ProfessionJob(
        name=name,
        effects_on_acquire=make_effects(**stats),
        effects_per_level=make_effects(**stats),  # consistent scaling
        crafting_tags=crafting or [],
        gathering_tags=gathering or [],
        economic_tags=economic or [],
    )

    register_profession(job)
    return job


# =========================
# DATA (CLEAN + SCALABLE)
# =========================

PROFESSION_DATA = {
    "Brewer": dict(stats=dict(constitution=1, perception=1), crafting=["brewing", "potions"]),
    "Carpenter": dict(stats=dict(dexterity=1, strength=1), crafting=["wood", "structures"]),
    "Cook": dict(stats=dict(luck=1, perception=1), crafting=["food"]),
    "Farmer": dict(stats=dict(constitution=1, wisdom=1), gathering=["plants", "crops"]),
    "Herbalist": dict(stats=dict(luck=1, wisdom=1), gathering=["herbs"], crafting=["potions"]),
    "Mason": dict(stats=dict(constitution=1, strength=1), crafting=["stone", "structures"]),
    "Midwife": dict(stats=dict(constitution=1, luck=1), crafting=["healing"]),
    "Miner": dict(stats=dict(dexterity=1, strength=1), gathering=["ore", "stone"]),
    "Sculptor": dict(stats=dict(dexterity=1, perception=1), crafting=["art", "stone"]),
    "Smith": dict(stats=dict(constitution=1, strength=1), crafting=["metal", "weapons", "armor"]),
    "Tailor": dict(stats=dict(dexterity=1, perception=1), crafting=["cloth", "armor"]),
    "Tanner": dict(stats=dict(agility=1, dexterity=1), crafting=["leather", "armor"]),
    "Tinker": dict(stats=dict(dexterity=1, intelligence=1), crafting=["tools", "gadgets"]),
}

# Build all professions

for name, data in PROFESSION_DATA.items():
    make_profession(
        name=name,
        stats=data["stats"],
        crafting=data.get("crafting"),
        gathering=data.get("gathering"),
        economic=data.get("economic"),
    )


# =========================
# UTILITIES
# =========================

def get_all_professions() -> List[ProfessionJob]:
    return list(PROFESSION_REGISTRY.values())
