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
    # (C) Creator
    "Animator": "C",
    "Conjuror": "C",
    "Elementalist": "C",
    "Necromancer": "C",
    # (D) Diva
    "Bard": "D",
    "Model": "D",
    "Ruler": "D",
    "Sensate": "D",
    # (E) Wanderer
    "Explorer": "E",
    "Mercenary": "E",
    "Merchant": "E",
    "Scout": "E",
    # (P) Priest
    "Cleric": "P",
    "Cultist": "P",
    "Oracle": "P",
    "Shaman": "P",
    # (R) Rogue
    "Assassin": "R",
    "Bandit": "R",
    "Burglar": "R",
    "Grifter": "R",
    # (S) Sage
    "Alchemist": "S",
    "Enchanter": "S",
    "Tamer": "S",
    "Wizard": "S",
    # (W) Warrior
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

    abilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "effects_on_acquire": [e.to_dict() for e in self.effects_on_acquire],
            "effects_per_level": [e.to_dict() for e in self.effects_per_level],
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

# Creator Jobs

# Animator: +3 DEX, INT, WIL
make_job(
    "Animator",
    effects_on_acquire = make_effects(
        dexterity = 3,
        intelligence = 3,
        willpower = 3,
    ),
    tags=["ranged", "warrior"]
)

# Conjuror: +3 CHA, INT, WIL
make_job(
    "Conjuror",
    effects_on_acquire = make_effects(
        charisma = 3,
        intelligence = 3,
        willpower = 3,
    ),
    tags=["ranged", "warrior"]
)

# Elementalist: +3 CON, INT, WIL
make_job(
    "Elementalist",
    effects_on_acquire = make_effects(
        constitution = 3,
        intelligence = 3,
        willpower = 3,
    ),
    tags=["ranged", "warrior"]
)

# Necromancer: +3 INT, WIL, WIS
make_job(
    "Necromancer",
    effects_on_acquire = make_effects(
        intelligence = 3,
        willpower = 3,
        wisdom = 3,
    ),
    tags=["ranged", "warrior"]
)

# Diva Jobs

# Bard: +3 CHA, DEX, LUC
make_job(
    "Bard",
    effects_on_acquire = make_effects(
        charisma = 3,
        dexterity = 3,
        luck = 3,
    ),
    tags=["ranged", "warrior"]
)

# Model: +3 AGI, CHA, PER
make_job(
    "Model",
    effects_on_acquire = make_effects(
        agility = 3,
        charisma = 3,
        perception = 3,
    ),
    tags=["ranged", "warrior"]
)

# Ruler: +3 CHA, WIS, LUC
make_job(
    "Ruler",
    effects_on_acquire = make_effects(
        charisma = 3,
        wisdom = 3,
        luck = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)

# Sensate: +3 CHA, INT, PER
make_job(
    "Sensate",
    effects_on_acquire = make_effects(
        charisma = 3,
        intelligence = 3,
        perception = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)
# Wanderer Jobs

# Explorer: +3 CON, INT, WIL
make_job(
    "Explorer",
    effects_on_acquire = make_effects(
        constitution = 3,
        intelligence = 3,
        willpower = 3,
    ),
    tags=["ranged", "warrior"]
)

# Merchant: +3 CHA, INT, PER
make_job(
    "Merchant",
    effects_on_acquire = make_effects(
        charisma = 3,
        intelligence = 3,
        perception = 3,
        ),
    tags=["melee", "aggressive", "warrior"]
)

# Mercenary: +3 DEX, PER, STR
make_job(
    "Mercenary",
    effects_on_acquire = make_effects(
        dexterity = 3,
        perception = 3,
        strength = 3,
        ),
    tags=["melee", "precision", "warrior"]
)

# Scout: +3 AGI, PER, WIS
make_job(
    "Scout",
    effects_on_acquire = make_effects(
        agility = 3,
        perception = 3,
        wisdom = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)

# Priest Jobs

# Cleric: +3 CON, LUC, WIS
make_job(
    "Cleric",
    effects_on_acquire = make_effects(
        constitution = 3,
        luck = 3,
        wisdom = 3,
    ),
    tags=["ranged", "warrior"]
)

# Cultist: +3 CHA, INT, LUC
make_job(
    "Cultist",
    effects_on_acquire = make_effects(
        charisma = 3,
        intelligence = 3,
        luck = 3,
        ),
    tags=["melee", "aggressive", "warrior"]
)

# Oracle: +3 CHA, LUC, WIS
make_job(
    "Oracle",
    effects_on_acquire = make_effects(
        charisma = 3,
        luck = 3,
        wisdom = 3,
        ),
    tags=["melee", "precision", "warrior"]
)

# Shaman: +3 LUC, STR, WIS
make_job(
    "Shaman",
    effects_on_acquire = make_effects(
        luck = 3,
        strength = 3,
        wisdom = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)

# Rogue

# Assassin: +3 AGI, CHA, DEX
make_job(
    "Assassin",
    effects_on_acquire = make_effects(
        agility = 3,
        charisma = 3,
        dexterity = 3,
    ),
    tags=["ranged", "warrior"]
)

# Bandit: +3 AGI, STR, WIS
make_job(
    "Bandit",
    effects_on_acquire = make_effects(
        agility = 3,
        strength = 3,
        wisdom = 3,
        ),
    tags=["melee", "aggressive", "warrior"]
)

# Burglar: +3 DEX, AGI, PER
make_job(
    "Burglar",
    effects_on_acquire = make_effects(
        dexterity = 3,
        perception = 3,
        agility = 3,
        ),
    tags=["melee", "precision", "warrior"]
)

# Grifter: +3 CHA, DEX, LUC
make_job(
    "Grifter",
    effects_on_acquire = make_effects(
        charisma = 3,
        dexterity = 3,
        luck = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)

# Sage Jobs

# Alchemist: +3 CON, DEX, INT
make_job(
    "Alchemist",
    effects_on_acquire = make_effects(
        constitution = 3,
        intelligence = 3,
        dexterity = 3,
    ),
    tags=["ranged", "warrior"]
)

# Enchanter: +3 DEX, INT, WIL
make_job(
    "Enchanter",
    effects_on_acquire = make_effects(
        dexterity = 3,
        intelligence = 3,
        willpower = 3,
        ),
    tags=["melee", "aggressive", "warrior"]
)

# Tamer: +3 CHA, CON, PER
make_job(
    "Tamer",
    effects_on_acquire = make_effects(
        charisma = 3,
        perception = 3,
        constitution = 3,
        ),
    tags=["melee", "precision", "warrior"]
)

# Wizard: +3 INT, WIL, WIS
make_job(
    "Wizard",
    effects_on_acquire = make_effects(
        intelligence = 3,
        willpower = 3,
        wisdom = 3,
        ),
    tags=["melee", "defensive", "warrior"]
)

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
    jobs_by_class = {}

    for job in JOB_REGISTRY.values():
        jobs_by_class.setdefault(job.job_class, []).append(job)
    return jobs_by_class
