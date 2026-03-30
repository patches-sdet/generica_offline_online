from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, DefaultDict, Any
from collections import defaultdict

from domain.attributes import Attributes, Defenses
from domain.race import Race
from domain.adventure import AdventureJob
from domain.profession import ProfessionJob
from domain.effects.base import Effect, EffectContext

if TYPE_CHECKING:
    from domain.abilities.factory import Ability


@dataclass(slots=True)
class Character:
    name: str

    # IDENTITY

    race: Race
    race_levels: dict[str, int] = field(default_factory=dict)
    base_race_levels: dict[str, int] = field(default_factory=dict)

    adventure_jobs: list[AdventureJob] = field(default_factory=list)
    adventure_levels: dict[str, int] = field(default_factory=dict)

    profession_jobs: list[ProfessionJob] = field(default_factory=list)
    profession_levels: dict[str, int] = field(default_factory=dict)

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
        def apply(self, context: EffectContext):
            for target in context.targets:
                success = target.modify_resource(self.pool, -self.amount)

                if not success:
                    raise ValueError(f"Not enough {self.pool} to spend {self.amount}")

        return self.modify_resource(pool, -amount)

    # HELPERS

    def get_skill(self, name: str) -> int:
        return self.skills.get(name, 0)

    def get_race_levels(self) -> int:
        return self.race_levels.get(self.race.name, 1)

    def has_adventure_job(self, job_name: str) -> bool:
        return any(job.name == job_name for job in self.adventure_jobs)

    def get_adventure_level_by_name(self, job_name: AdventureJob) -> int:
        return self.adventure_levels.get(job_name, 1)

    def get_profession_level_by_name(self, job_name: ProfessionJob) -> int:
        return self.profession_levels.get(job_name, 1)

    # SERIALIZATION (FIXED)

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
