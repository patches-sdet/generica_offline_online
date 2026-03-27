from dataclasses import dataclass
from typing import Callable, List, Optional

from domain.effects.base import Effect


@dataclass
class Ability:
    name: str
    unlock_condition: Callable

    # Execution
    execute: Optional[Callable] = None
    effect_generator: Optional[Callable] = None

    # Metadata
    cost: int = 0
    cost_pool: Optional[str] = None
    duration: Optional[str] = None
    description: str = ""

    # Flags
    is_passive: bool = False
    is_skill: bool = False
    target_type: str = "self"


# =========================================================
# Factory
# =========================================================

def make_ability(
    *,
    name: str,
    unlock_condition: Callable,
    execute: Optional[Callable] = None,
    effect_generator: Optional[Callable] = None,
    cost: int = 0,
    cost_pool: Optional[str] = None,
    duration: Optional[str] = None,
    description: str = "",
    is_passive: bool = False,
    is_skill: bool = False,
    target_type: str = "self",
):
    # ===============================
    # Validation
    # ===============================

    if execute and effect_generator:
        raise ValueError(f"{name}: Cannot define both execute and effect_generator")

    if is_passive and execute:
        raise ValueError(f"{name}: Passive abilities cannot define execute")

    if not is_passive and not execute:
        raise ValueError(f"{name}: Active abilities must define execute")

    ability = Ability(
        name=name,
        unlock_condition=unlock_condition,
        execute=execute,
        effect_generator=effect_generator,
        cost=cost,
        cost_pool=cost_pool,
        duration=duration,
        description=description,
        is_passive=is_passive,
        is_skill=is_skill,
        target_type=target_type,
    )

    from .registry import register_ability
    register_ability(ability)

    return ability
