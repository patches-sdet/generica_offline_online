from dataclasses import dataclass, field
from typing import Dict, List
from domain.effects import Effect, make_effects

# Class Registry

CLASS_REGISTRY = {
    "S": "Sage",
    "C": "Creator",
    "W": "Warrior",
    "R": "Rogue",
    "D": "Diva",
    "P": "Priest",
    "E": "Wanderer",
}

# Job to Class Map

JOB_CLASS_MAP = {
    # Warrior
    "Archer": "W",
    "Berserker": "W",
    "Duelist": "W",
    "Knight": "W",
}


# Core Adventure Job Dataclass

@dataclass (frozen=True)
class AdventureJob:
    name: str

    # One-time stat bonuses on acquisition
    effects_on_acquire: List[Effect] = field(default_factory=list)
    effects_per_level: List[Effect] = field(default_factory=list)

    # Future systems
    pool_modifiers: Dict[str, float] = field(default_factory=dict)
    defense_modifiers: Dict[str, int] = field(default_factory=dict)

    abilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
            "pool_modifiers": self.pool_modifiers,
            "defense_modifiers": self.defense_modifiers,
            "abilities": self.abilities,
            "tags": self.tags,
        }

# Derived Properties

    @property
    def class_code(self) -> str:
        return JOB_CLASS_MAP[self.name]

    @property
    def job_class(self) -> str:
        return CLASS_REGISTRY[self.class_code]

# Application Methods

    def make_effects(**mods):
        return [StatIncrease(stat, value) for stat, value in mods.items()]

    def apply_to_pools(self, pools: Dict[str, tuple]):
        """
        Placeholder for future expansion.
        """
        for pool, multiplier in self.pool_modifiers.items():
            current, max_val = pools[pool]
            new_max = int(max_val * multiplier)
            pools[pool] = (current, new_max)

    def apply_to_defenses(self, defenses: Dict[str, int]):
        """
        Placeholder for future expansion.
        """
        for defense, value in self.defense_modifiers.items():
            defenses[defense] += value


# Job Registry

JOB_REGISTRY: Dict[str, "AdventureJob"] = {}


def register_job(job: AdventureJob):
    JOB_REGISTRY[job.name.lower()] = job


def resolve_job(name: str) -> AdventureJob:
    job = JOB_REGISTRY.get(name.lower())
    if not job:
        raise ValueError(f"Unknown job: {name}")
    return job

# Factory Helper

def make_job(name: str, **kwargs) -> AdventureJob:
    if name not in JOB_CLASS_MAP:
        raise ValueError(f"{name} is not defined in JOB_CLASS_MAP")

    job = AdventureJob(name=name, **kwargs)
    register_job(job)
    return job

# Warrior Jobs

# Archer: +3 DEX, PER, STR
make_job(
    "Archer",
    effects_on_acquire = make_effects(
        dexterity = 3,
        perception = 3,
        strength = 3,
    ),
    tags=["ranged", "warrior"]
)

# Berserker: +3 CON, STR, WILL
make_job(
    "Berserker",
    effects_on_acquire = make_effects(
        constitution = 3,
        strength = 3,
        willpower = 3,
        ),
    tags=["melee", "aggressive", "warrior"]
)

# Duelist: +3 AGL, DEX, STR
make_job(
    "Duelist",
    effects_on_acquire = make_effects(
        agility = 3,
        dexterity = 3,
        strength = 3,
        ),
    tags=["melee", "precision", "warrior"]
)

# Knight: +3 CHA, CON, STR
make_job(
    "Knight",
    effects_on_acquire = make_effects(
        charisma = 3,
        constitution = 3,
        strength = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)

# Utility Functions

def get_jobs_by_class(class_code: str) -> List[AdventureJob]:
    return [
        job
        for job in JOB_REGISTRY.values()
        if job.class_code == class_code
    ]

def get_all_jobs() -> List[AdventureJob]:
    return list(JOB_REGISTRY.values())

def get_jobs_grouped_by_class() -> Dict[str, List[AdventureJob]]:
    print("DEBUG: function called")
    jobs_by_class = {}

    for job in JOB_REGISTRY.values():
        jobs_by_class.setdefault(job.job_class, []).append(job)
    return jobs_by_class
