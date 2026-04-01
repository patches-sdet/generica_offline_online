from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True, slots=True)
class Ability:
    name: str
    unlock_condition: Callable
    execute: Optional[Callable] = None
    effect_generator: Optional[Callable] = None

    cost: Optional[int] = 0
    cost_pool: Optional[str] = None
    duration: Optional[str] = None
    description: str = ""
    is_passive: bool = False
    is_skill: bool = False
    target_type: str = "self"
    scales_with_level: bool = True

    def is_unlocked(self, character) -> bool:
        return self.unlock_condition(character)

def validate_ability_definition(
    *,
    name: str,
    execute: Optional[Callable],
    effect_generator: Optional[Callable],
    is_passive: bool,
) -> None:
    if execute and effect_generator:
        raise ValueError(
            f"{name}: Cannot define both execute and effect_generator"
        )

    if not execute and not effect_generator:
        raise ValueError(
            f"{name}: Must define either execute or effect_generator"
        )

    if is_passive and execute:
        raise ValueError(
            f"{name}: Passive abilities cannot define execute"
        )

def make_ability(
    *,
    name: str,
    unlock_condition: Callable,
    execute: Optional[Callable] = None,
    effect_generator: Optional[Callable] = None,
    cost: Optional[int] = 0,
    cost_pool: Optional[str] = None,
    duration: Optional[str] = None,
    description: str = "",
    is_passive: bool = False,
    is_skill: bool = False,
    target_type: str = "self",
    scales_with_level: bool = True,
    auto_register: bool = True,
) -> Ability:
    validate_ability_definition(
        name=name,
        execute=execute,
        effect_generator=effect_generator,
        is_passive=is_passive,
    )
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
        scales_with_level=scales_with_level,
    )

    if auto_register:
        from domain.content_registry import register_ability
        register_ability(ability)

    return ability