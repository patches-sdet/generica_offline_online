from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING, DefaultDict
from collections import defaultdict

from domain.attributes import Attributes
from domain.race import Race
from domain.adventure import AdventureJob

if TYPE_CHECKING:
    from domain.abilities import Ability


@dataclass(slots=True)
class Character:
    name: str

    race: Race
    race_level: int

    adventure_job: AdventureJob
    adventure_level: int

    profession_job: Optional[AdventureJob] = None
    profession_level: int = 0

    attributes: Optional[Attributes] = None

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
            "race_level": self.race_level,
            "adventure_job": self.adventure_job.to_dict(),
            "adventure_level": self.adventure_level,
            "profession_job": (
                self.profession_job.to_dict() if self.profession_job else None
            ),
            "profession_level": self.profession_level,
            "attributes": self.attributes.to_dict(),

            "current_hp": self.current_hp,
            "current_sanity": self.current_sanity,
            "current_stamina": self.current_stamina,
            "current_moxie": self.current_moxie,
            "current_fortune": self.current_fortune,
        }
