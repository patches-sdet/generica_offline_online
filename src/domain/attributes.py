from dataclasses import dataclass
from typing import Tuple, Dict

# Default Attributes

DEFAULT_STATS = {
    "strength": 25,
    "constitution": 25,
    "intelligence": 25,
    "wisdom": 25,
    "dexterity": 25,
    "agility": 25,
    "charisma": 25,
    "willpower": 25,
    "perception": 25,
    "luck": 25,
}

ATTRIBUTE_NAMES = list(DEFAULT_STATS.keys())

# Core Attributes

@dataclass
class Attributes:
    strength: int
    constitution: int
    intelligence: int
    wisdom: int
    dexterity: int
    agility: int
    charisma: int
    willpower: int
    perception: int
    luck: int

    race: str

    adventure_job: str | None
    adventure_level: int

    craft_job: str | None
    craft_level: int

# Derived Stats

STAT_FORMULAS = {
    "hp": lambda a: a.strength + a.constitution,
    "sanity": lambda a: a.intelligence + a.wisdom,
    "stamina": lambda a: a.strength + a.agility,
    "moxie": lambda a: a.charisma + a.willpower,
    "fortune": lambda a: a.perception + a.luck,
}

@dataclass
class Pools:
    hp: Tuple[int, int]
    sanity: Tuple[int, int]
    stamina: Tuple[int, int]
    moxie: Tuple[int, int]
    fortune: Tuple[int, int]

# Calculated Pools

def calculate_pools(attrs: Attributes) -> Pools:
    """
    Generate resource pools based on attribute formulas.
    Pools are returned as (current, max).
    """

    hp = STAT_FORMULAS["hp"](attrs)
    sanity = STAT_FORMULAS["sanity"](attrs)
    stamina = STAT_FORMULAS["stamina"](attrs)
    moxie = STAT_FORMULAS["moxie"](attrs)
    fortune = STAT_FORMULAS["fortune"](attrs)

    return Pools(
        hp=(hp, hp),
        sanity=(sanity, sanity),
        stamina=(stamina, stamina),
        moxie=(moxie, moxie),
        fortune=(fortune, fortune),
    )

@dataclass
class Defenses:
    armor: int
    mental_fortitude: int
    endurance: int
    cool: int
    fate: int

# Pool Manager (runtime gameplay manipulation)

class PoolManager:
    """
    Utility class to manage resource pools during gameplay.
    Handles damage, recovery, and spending resources.
    """

    def __init__(self, pools: Pools):
        self.pools = pools

    def _modify_pool(self, pool_name: str, amount: int):
        current, maximum = getattr(self.pools, pool_name)
        new_value = max(0, min(maximum, current + amount))
        setattr(self.pools, pool_name, (new_value, maximum))

    def damage(self, pool_name: str, amount: int):
        """Reduce a pool value."""
        self._modify_pool(pool_name, -amount)

    def heal(self, pool_name: str, amount: int):
        """Increase a pool value."""
        self._modify_pool(pool_name, amount)

    def spend(self, pool_name: str, amount: int) -> bool:
        """
        Spend a resource if available.
        Returns True if successful.
        """
        current, _ = getattr(self.pools, pool_name)

        if current < amount:
            return False

        self._modify_pool(pool_name, -amount)
        return True
