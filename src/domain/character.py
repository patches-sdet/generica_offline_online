from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING, DefaultDict
from collections import defaultdict

from domain.attributes import Attributes
from domain.race import Race
from domain.adventure import AdventureJob
from domain.effects import Effect
from domain.profession import ProfessionJob

if TYPE_CHECKING:
    from domain.abilities import Ability


@dataclass(slots=True)
class Character:
    name: str

    race: Race
    race_levels: dict[str, int] = field(default_factory=dict)
    base_race_levels: dict[str, int] = field(default_factory=dict)

    adventure_jobs: list[AdventureJob] = field(default_factory=list)
    adventure_levels: dict[str, int] = field(default_factory=dict)

    profession_jobs: list[ProfessionJob] = field(default_factory=list)
    profession_levels: dict[str, int] = field(default_factory=dict)
    
    attributes: Attributes | None = field(default=None, init=False)
    attribute_effects: list[Effect] = field(default_factory=list)

    # Base snapshot for delta display
    _base_attributes: dict = field(default_factory=dict, init=False)

    # Source tracking (FIXED)
    _attribute_sources: DefaultDict[str, DefaultDict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int)),
        init=False
    )

    # Current resource pools
    current_hp: int = 0
    current_sanity: int = 0
    current_stamina: int = 0
    current_moxie: int = 0
    current_fortune: int = 0

    # Skill Management
    skills: dict[str,int] = field(default_factory=dict)

    # Abilities
    abilities: List["Ability"] = field(default_factory=list)
    ability_levels: dict[str, int] = field(default_factory=dict)

    # Derived stat tracking
    _derived_bonuses: dict = field(default_factory=dict, init=False)
    _derived_overrides: dict = field(default_factory=dict, init=False)

    # -------------------------
    # ATTRIBUTE MUTATION API
    # -------------------------

    def add_attribute(self, attr: str, value: int, source: str | None = None):
        if not hasattr(self.attributes, attr):
            raise ValueError(f"Invalid attribute: {attr}")

        current = getattr(self.attributes, attr)
        setattr(self.attributes, attr, current + value)

        if source:
            self._attribute_sources[attr][source] += value

    # -------------------------

    def to_dict(self):
        return {
            "name": self.name,
            "race": self.race.to_dict(),
            "race_levels": self.race_levels,
            "adventure_jobs": self.adventure_jobs.to_dict(),
            "adventure_levels": self.adventure_levels,
            "profession_jobs": self.profession_jobs.to_dict(),
            "profession_levels": self.profession_levels,
            "attributes": self.attributes.to_dict(),
            "skills": self.skills,
            "current_hp": self.current_hp,
            "current_sanity": self.current_sanity,
            "current_stamina": self.current_stamina,
            "current_moxie": self.current_moxie,
            "current_fortune": self.current_fortune,
        }

    def get_skill(self, name: str) -> int:
        return self.skills.get(name, 0)

    def get_race_level(self) -> int:
        return self.race_levels.get(self.race.name, 1)

    def has_adventure_job(self, job_name: str) -> bool:
        return any(job.name == job_name for job in self.adventure_jobs)

    def get_adventure_level_by_name(self, job_name: str) -> int:
        return self.adventure_levels.get(job_name, 0)
