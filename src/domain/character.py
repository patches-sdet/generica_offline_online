from dataclasses import dataclass
from .attributes import Attributes, Pools, Defenses, PoolManager

@dataclass
class Character:
    name: str
    attributes: Attributes
    pools: Pools
    defenses: Defenses

    @property
    def pool_manager(self):
        return PoolManager(self.pools)
