from dataclasses import dataclass
from .attributes import Attributes, Pools, Defenses, PoolManager
from .race import Race
from .adventure import AdventureJob

@dataclass
class Character:
    name: str
    race: Race
    job: AdventureJob
    attributes: Attributes
    pools: Pools
    defenses: Defenses

    @property
    def pool_manager(self):
        return PoolManager(self.pools)
