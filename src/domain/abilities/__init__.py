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
    is_passive: bool = True
    is_skill: bool = False
    effect_generator: Callable[["Character"], List[Effect]] | None = None

    cost: int | None = None
    cost_pool: str = None
    duration: str | None = None
    description: str | None = None

    execute: Callable[["Character", list["Character"]], None] | None = None

    def get_effects(self, character: "Character") -> List[Effect]:
        if self.effect_generator and self.effects:
            raise ValueError(
                    f"Ability '{self.name}' defines both effects and effect_generator"
                    )

        if self.effect_generator:
            return self.effect_generator(character)

        return self.effects


ALL_ABILITIES = []


def register_ability(ability):
    ALL_ABILITIES.append(ability)

def requires_job(job_name: str, min_level: int = 1):
    def condition(c):
        return (
                any(job.name == job_name for job in c.adventure_jobs)
                and c.adventure_levels.get(job_name, 0) >= min_level
                )
    return condition

def make_ability(*, 
                 name: str, 
                 unlock_condition, 
                 effects=None, 
                 effect_generator=None, 
                 cost=None, 
                 cost_pool=None,
                 duration=None, 
                 description=None,
                 execute=None,
                 is_passive=True,
                 is_skill=False):
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
        is_passive=is_passive,
        is_skill=is_skill,
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
