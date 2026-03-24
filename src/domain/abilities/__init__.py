from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING, List
from domain.effects import Effect

if TYPE_CHECKING:
    from domain.character import Character


@dataclass(frozen=True)
class Ability:
    name: str
    unlock_condition: Callable[["Character"], bool]
    effects: list[Effect] = field(default_factory=list)
    effect_generator: Callable[["Character"], List[Effect]] | None = None

    cost: int | None = None
    cost_pool: str = None
    duration: str | None = None
    description: str | None = None

    execute: Callable[["Character"], None] | None = None

    def get_effects(self, character: "Character") -> List[Effect]:
        if self.effect_generator:
            return self.effect_generator(character)
        return self.effects


ALL_ABILITIES = []


def register_ability(ability):
    ALL_ABILITIES.append(ability)


def make_ability(*, 
                 name: str, 
                 unlock_condition, 
                 effects=None, 
                 effect_generator=None, 
                 cost=None, 
                 cost_pool=None,
                 duration=None, 
                 description=None,
                 execute=None):
    ability = Ability(
        name=name,
        unlock_condition=unlock_condition,
        effects=effects or [],
        effect_generator=effect_generator,
        cost=cost,
        cost_pool=cost_pool,
        duration=duration,
        description=description,
        execute=execute,
    )
    register_ability(ability)
    return ability

import pkgutil
import importlib

def _auto_register_abilities():
    """
    Auto-discover and register all valid ability modules.
    each module must define its 'register()' function.
    """

    for module_info in pkgutil.iter_modules(__path__):
        module_name = module_info.name

        if module_name.startswith("_"):
            continue

        module = importlib.import_module(f"{__name__}.{module_name}")

        if hasattr(module, "register"):
            module.register()

# runs on import
_auto_register_abilities()
