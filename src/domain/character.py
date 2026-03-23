from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING, DefaultDict
from collections import defaultdict

if TYPE_CHECKING:
    from domain.abilities import Ability

from .attributes import Attributes
from .race import Race
from .adventure import AdventureJob


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
    _base_attributes: dict = field(default_factory = dict, init = False)
    _attribute_sources: DefaultDict[str, DefaultDict[str, int]] = field(
            default_factory = lambda: defaultdict(lambda: defaultdict(int)), init = False)

    current_hp: int = 0
    current_sanity: int = 0
    current_stamina: int = 0
    current_moxie: int = 0
    current_fortune: int = 0

    abilities: List["Ability"] = field(default_factory=list)
    ability_levels: dict[str, int] = field(default_factory=dict)


    _derived_bonuses: dict = None
    _derived_overrides: dict = None

    def __post_init__(self):
        if self._derived_bonuses is None:
            self._derived_bonuses = {}

        if self._derived_overrides is None:
            self._derived_overrides = {}

        if not isinstance(self._attribute_sources, dict):
            self._attribute_sources = defaultdict(lambda: defaultdict(int))

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

    def add_attribute(self, attr: str, value: int, source: str = None):
        if not hasattr(self.attributes, attr):
            raise ValueError(f"Invalid attribute: {attr}")

        current = getattr(self.attributes, attr)
        setattr(self.attributes, attr, current + value)

        if source:
            self._attribute_sources[attr][source] += value
