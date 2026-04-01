from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, DefaultDict, Any
from collections import defaultdict

from domain.attributes import Attributes, Defenses
from domain.race import Race
from domain.adventure import AdventureJob
from domain.profession import ProfessionJob
from domain.progression import Progression
from domain.effects.base import Effect

if TYPE_CHECKING:
    from domain.abilities.factory import Ability


@dataclass(slots=True)
class Character:
    name: str

    # IDENTITY
    race_bases: List[str] = field(default_factory=list)
    race_template: Optional[str] = None
    progressions: dict[tuple[str, str], Progression] = field(default_factory=dict)

    # CORE STATS

    attributes: Attributes = field(default_factory=Attributes)
    defenses: Defenses = field(default=None)
    attribute_effects: list[Effect] = field(default_factory=list)

    # Snapshot (for debug/diff)
    _base_attributes: dict = field(default_factory=dict, init=False)

    # Source tracking (your original feature preserved)
    _attribute_sources: DefaultDict[str, DefaultDict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int)),
        init=False
    )

    # RUNTIME SYSTEMS

    states: dict[str, Any] = field(default_factory=dict)
    tags: set = field(default_factory=set)
    event_listeners: list[Any] = field(default_factory=list)

    # Combat modifiers
    roll_modifiers: list[Any] = field(default_factory=list)
    next_attack_modifiers: list[Any] = field(default_factory=list)
    extra_attacks: int = 0
    bonus_damage: int = 0
    damage_conversion: Any = None

    # Inventory
    inventory: list[Any] = field(default_factory=list)

    # RESOURCES

    current_hp: int = 0
    current_sanity: int = 0
    current_stamina: int = 0
    current_moxie: int = 0
    current_fortune: int = 0

    # SKILLS & ABILITIES

    skills: dict[str, int] = field(default_factory=dict)

    # NOTE: abilities list is optional now (registry is primary)
    abilities: List["Ability"] = field(default_factory=list)
    ability_levels: dict[str, int] = field(default_factory=dict)

    # DERIVED STAT TRACKING

    _derived_bonuses: defaultdict[str, int] = field(default_factory=lambda: defaultdict(int), init=False)
    _derived_overrides: dict = field(default_factory=dict, init=False)

    # ATTRIBUTE API

    def add_stat(self, stat: str, value: int, source: str | None = None):
        self.attributes.add(stat, value)

        if source:
            self._attribute_sources[stat][source] += value

    def set_stat(self, stat: str, value: int):
        self.attributes.set(stat, value)

    def get_stat(self, stat: str) -> int:
        return self.attributes.get(stat)

    # RESOURCE API

    def modify_resource(self, pool: str, amount: int) -> bool:
        attr = f"current_{pool}"

        if not hasattr(self, attr):
            raise ValueError(f"Invalid resource pool: {pool}")

        current = getattr(self, attr)
        new_value = current + amount

        # Prevent going below 0
        if new_value < 0:
            return False

        # OPTIONAL: clamp to max
        max_attr = f"max_{pool}"
        if hasattr(self, max_attr):
            new_value = min(new_value, getattr(self, max_attr))

        setattr(self, attr, new_value)
        return True


    def spend_resource(self, pool: str, amount: int) -> bool:
        return self.modify_resource(pool, -amount)

    # HELPERS
    def get_progression_level(self, name: str, type: str) -> int:
        p = self.progressions.get((type, name))
        return p.level if p else 0
    
    def get_skill(self, name: str) -> int:
        return self.skills.get(name, 0)

    def get_race_levels(self) -> int:
        return self.get_race_level(self.race.name)

    def has_adventure_job(self, job_name: str) -> bool:
        return any(job.name == job_name for job in self.adventure_jobs)
    
    def get_race_level(self, race_name: str) -> int:
        return self.get_progression_level(race_name, "race")

    def get_adventure_level_by_name(self, job_name, default=0):
        level = self.get_progression_level(job_name, "adventure")
        return level if level else default

    def get_profession_level_by_name(self, job_name, default=0):
        level = self.get_progression_level(job_name, "profession")
        return level if level else default
    
    def get_advancecd_level_by_name(self, job_name, default=0):
        level = self.get_progression_level(job_name, "advanced")
        return level if level else default
    
    # SERIALIZATION

    def to_dict(self):
        return {
            "name": self.name,
            "race": self.race.name,
            "race_levels": self.race_levels,
            "adventure_jobs": [job.name for job in self.adventure_jobs],
            "adventure_levels": self.adventure_levels,
            "profession_jobs": [job.name for job in self.profession_jobs],
            "profession_levels": self.profession_levels,
            "attributes": self.attributes.to_dict(),
            "skills": self.skills,
            "resources": {
                "hp": self.current_hp,
                "sanity": self.current_sanity,
                "stamina": self.current_stamina,
                "moxie": self.current_moxie,
                "fortune": self.current_fortune,
            },
        }
