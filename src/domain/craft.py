from dataclasses import dataclass, field
from typing import Dict, List
from domain.effects import Effect, make_effects

@dataclass(frozen=True)
class ProfessionJob:
    name: str

    effects_on_acquire: List[Effect] = field(default_factory=list)
    effects_per_level: List[Effect] = field(default_factory=list)

    abilities: List[str] = field(default_factory=list)

    # Future systems
    crafting_tags: List[str] = field(default_factory=list)
    gathering_tags: List[str] = field(default_factory=list)
    economic_tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
            "abilities": self.abilities,
            "crafting_tags": self.crafting_tags,
            "gathering_tags": self.gathering_tags,
            "economic_tags": self.economic_tags,
        }

PROFESSION_REGISTRY: Dict[str, ProfessionJob] = {}


def register_profession(job: ProfessionJob):
    PROFESSION_REGISTRY[job.name.lower()] = job


def resolve_profession(name: str) -> ProfessionJob:
    job = PROFESSION_REGISTRY.get(name.lower())
    if not job:
        raise ValueError(f"Unknown profession: {name}")
    return job


def make_profession(name: str, **kwargs) -> ProfessionJob:
    job = ProfessionJob(name=name, **kwargs)
    register_profession(job)
    return job

# Profession Jobs

make_profession(
    "Brewer",
    effects_on_acquire=make_effects(constitution=1, perception=1),
    effects_per_level=make_effects(constitution=1, perception=1),
    crafting_tags=["brewing", "potions"]
)

make_profession(
    "Carpenter",
    effects_on_acquire=make_effects(dexterity=1, strength=1),
    effects_per_level=make_effects(dexterity=1, strength=1),
    crafting_tags=["wood", "structures"]
)

make_profession(
    "Cook",
    effects_on_acquire=make_effects(luck=1, perception=1),
    effects_per_level=make_effects(luck=1, perception=1),
    crafting_tags=["food"]
)

make_profession(
    "Farmer",
    effects_on_acquire=make_effects(constitution=1, wisdom=1),
    effects_per_level=make_effects(constitution=1, wisdom=1),
    gathering_tags=["plants", "crops"]
)

make_profession(
    "Herbalist",
    effects_on_acquire=make_effects(luck=1, wisdom=1),
    effects_per_level=make_effects(luck=1, wisdom=1),
    gathering_tags=["herbs"],
    crafting_tags=["potions"]
)

make_profession(
    "Mason",
    effects_on_acquire=make_effects(constitution=1, strength=1),
    effects_per_level=make_effects(constitution=1, strength=1),
    crafting_tags=["stone", "structures"]
)

make_profession(
    "Midwife",
    effects_on_acquire=make_effects(constitution=1, luck=1),
    effects_per_level=make_effects(constitution=1, luck=1),
    crafting_tags=["healing"]
)

make_profession(
    "Miner",
    effects_on_acquire=make_effects(dexterity=1, strength=1),
    effects_per_level=make_effects(dexterity=1, strength=1),
    gathering_tags=["ore", "stone"]
)

make_profession(
    "Sculptor",
    effects_on_acquire=make_effects(dexterity=1, perception=1),
    effects_per_level=make_effects(dexterity=1, perception=1),
    crafting_tags=["art", "stone"]
)

make_profession(
    "Smith",
    effects_on_acquire=make_effects(constitution=1, strength=1),
    effects_per_level=make_effects(constitution=1, strength=1),
    crafting_tags=["metal", "weapons", "armor"]
)

make_profession(
    "Tailor",
    effects_on_acquire=make_effects(dexterity=1, perception=1),
    effects_per_level=make_effects(dexterity=1, perception=1),
    crafting_tags=["cloth", "armor"]
)

make_profession(
    "Tanner",
    effects_on_acquire=make_effects(agility=1, dexterity=1),
    effects_per_level=make_effects(agility=1, dexterity=1),
    crafting_tags=["leather", "armor"]
)

make_profession(
    "Tinker",
    effects_on_acquire=make_effects(dexterity=1, intelligence=1),
    effects_per_level=make_effects(dexterity=1, intelligence=1),
    crafting_tags=["tools", "gadgets"]
)

def get_all_professions() -> List[ProfessionJob]:
    return list(PROFESSION_REGISTRY.values())
