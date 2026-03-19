from dataclasses import dataclass
from .attributes import Attributes, Pools, Defenses, PoolManager
from .race import Race
from .adventure import AdventureJob

@dataclass
class Character:
    name: str
    race: Race
#    race_level: RaceLevel
    adventure_job: AdventureJob
#    adventure_level:AdventureLevel
#    profession_job: ProfessionJob
#    profession_level: ProfessionLevel
    attributes: Attributes
    pools: Pools
    defenses: Defenses

    @property
    def pool_manager(self):
        return PoolManager(self.pools)
