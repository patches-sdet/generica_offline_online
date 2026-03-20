from dataclasses import dataclass
from typing import Optional

from .attributes import Attributes, Pools, Defenses, PoolManager
from .race import Race
from .adventure import AdventureJob

@dataclass
class Character:
    name: str

    race: Race
    race_level: int
    
    adventure_job: AdventureJob
    adventure_level: int
    
    profession_job: Optional[AdventureJob] = None
    profession_level: int = 0
    
    attributes: Attributes = None

    current_hp: int = 0
    current_sanity: int = 0
    current_stamina: int = 0
    current_moxie: int = 0
    current_fortune: int = 0

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
        }
