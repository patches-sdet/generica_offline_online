from dataclasses import dataclass, field
from typing import Dict, List

from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease


# Class connection

CLASS_REGISTRY = {
    "S": "Sage",
    "C": "Creator",
    "W": "Warrior",
    "R": "Rogue",
    "D": "Diva",
    "P": "Priest",
    "E": "Wanderer",
}

JOB_CLASS_MAP = {
    "Alchemist": "S",
    "Animator": "C",
    "Archer": "W",
    "Assassin": "R",
    "Bandit": "R",
    "Bard": "D",
    "Berserker": "W",
    "Burglar": "R",
    "Cleric": "P",
    "Conjuror": "C",
    "Cultist": "P",
    "Duelist": "W",
    "Elementalist": "C",
    "Enchanter": "S",
    "Explorer": "E",
    "Grifter": "R",
    "Knight": "W",
    "Mercenary": "E",
    "Merchant": "E",
    "Model": "D",
    "Necromancer": "C",
    "Oracle": "P",
    "Ruler": "D",
    "Scout": "E",
    "Sensate": "D",
    "Shaman": "P",
    "Tamer": "S",
    "Wizard": "S",
}


# Core Job dataclass

@dataclass(frozen=True)
class AdventureJob:
    name: str

    effects_on_acquire: List[Effect] = field(default_factory=list)
    effects_per_level: List[Effect] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)

    def get_effects(self, level: int):
        level = max(1, level)

        effects = []
        effects.extend(self.effects_on_acquire)
        effects.extend(self.effects_per_level * (level - 1))

        return effects

    # CLASS HELPERS
    
    @property
    def class_code(self) -> str:
        return JOB_CLASS_MAP[self.name]

    @property
    def job_class(self) -> str:
        return CLASS_REGISTRY[self.class_code]

    # SERIALIZATION

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [str(e) for e in self.effects_on_acquire],
            "effects_per_level": [str(e) for e in self.effects_per_level],
            "tags": self.tags,
        }

# HELPERS

def make_effects(**mods):
    return [StatIncrease(stat, value) for stat, value in mods.items()]

# REGISTRY

JOB_REGISTRY: Dict[str, AdventureJob] = {}


def register_job(job: AdventureJob):
    JOB_REGISTRY[job.name.lower()] = job


def resolve_job(name: str) -> AdventureJob:
    job = JOB_REGISTRY.get(name.lower())
    if not job:
        raise ValueError(f"Unknown job: {name}")
    return job


def get_all_jobs() -> List[AdventureJob]:
    return list(JOB_REGISTRY.values())

# FACTORY

def make_job(name: str, stats: dict, tags: List[str]) -> AdventureJob:
    if name not in JOB_CLASS_MAP:
        raise ValueError(f"{name} not defined in JOB_CLASS_MAP")

    job = AdventureJob(
        name=name,
        effects_on_acquire=make_effects(**stats),
        effects_per_level=make_effects(**stats),
        tags=tags,
    )

    register_job(job)
    return job

# JOB DEFINITIONS

JOB_DATA = {
    "Animator": dict(stats=dict(dexterity=3, intelligence=3, willpower=3), tags=["creation", "minions", "support"]),
    "Conjuror": dict(stats=dict(charisma=3, intelligence=3, willpower=3), tags=["creation", "minions", "support"]),
    "Elementalist": dict(stats=dict(constitution=3, intelligence=3, willpower=3), tags=["damage", "minions", "support"]),
    "Necromancer": dict(stats=dict(intelligence=3, willpower=3, wisdom=3), tags=["creation", "minions", "support"]),

    "Bard": dict(stats=dict(charisma=3, dexterity=3, luck=3), tags=["support", "buffs", "debuff"]),
    "Model": dict(stats=dict(agility=3, charisma=3, perception=3), tags=["buffs", "social"]),
    "Ruler": dict(stats=dict(charisma=3, wisdom=3, luck=3), tags=["defensive"]),
    "Sensate": dict(stats=dict(charisma=3, intelligence=3, perception=3), tags=["defensive"]),

    "Explorer": dict(stats=dict(constitution=3, intelligence=3, willpower=3), tags=["ranged"]),
    "Merchant": dict(stats=dict(charisma=3, intelligence=3, perception=3), tags=["utility"]),
    "Mercenary": dict(stats=dict(dexterity=3, perception=3, strength=3), tags=["melee"]),
    "Scout": dict(stats=dict(agility=3, perception=3, wisdom=3), tags=["utility"]),

    "Cleric": dict(stats=dict(constitution=3, luck=3, wisdom=3), tags=["support", "healer", "buffs"]),
    "Cultist": dict(stats=dict(charisma=3, intelligence=3, luck=3), tags=["aggressive"]),
    "Oracle": dict(stats=dict(charisma=3, luck=3, wisdom=3), tags=["support"]),
    "Shaman": dict(stats=dict(luck=3, strength=3, wisdom=3), tags=["support"]),

    "Assassin": dict(stats=dict(agility=3, charisma=3, dexterity=3), tags=["precision"]),
    "Bandit": dict(stats=dict(agility=3, strength=3, wisdom=3), tags=["aggressive"]),
    "Burglar": dict(stats=dict(dexterity=3, perception=3, agility=3), tags=["precision"]),
    "Grifter": dict(stats=dict(charisma=3, dexterity=3, luck=3), tags=["utility"]),

    "Alchemist": dict(stats=dict(constitution=3, intelligence=3, dexterity=3), tags=["utility"]),
    "Enchanter": dict(stats=dict(dexterity=3, intelligence=3, willpower=3), tags=["aggressive"]),
    "Tamer": dict(stats=dict(charisma=3, perception=3, constitution=3), tags=["utility"]),
    "Wizard": dict(stats=dict(intelligence=3, willpower=3, wisdom=3), tags=["caster"]),

    "Archer": dict(stats=dict(dexterity=3, perception=3, strength=3), tags=["ranged"]),
    "Berserker": dict(stats=dict(constitution=3, strength=3, willpower=3), tags=["aggressive"]),
    "Duelist": dict(stats=dict(agility=3, dexterity=3, strength=3), tags=["precision"]),
    "Knight": dict(stats=dict(charisma=3, constitution=3, strength=3), tags=["defensive"]),
}


# Build registry

for name, data in JOB_DATA.items():
    make_job(name, stats=data["stats"], tags=data["tags"])

# UTILITIES

def get_jobs_by_class(class_code: str) -> List[AdventureJob]:
    return [job for job in JOB_REGISTRY.values() if job.class_code == class_code]


def get_jobs_grouped_by_class() -> Dict[str, List[AdventureJob]]:
    grouped: Dict[str, List[AdventureJob]] = {}

    for job in JOB_REGISTRY.values():
        grouped.setdefault(job.job_class, []).append(job)

    return grouped
