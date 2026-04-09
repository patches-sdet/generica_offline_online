from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True, slots=True)
class Ability:
    name: str
    unlock_condition: Callable
    execute: Callable | None = None
    effect_generator: Callable | None = None

    # Progression, scaling, and eventual metadata fields
    # required_level should not be in here, since it's dependent on the source that granted it. It's in teh grant registration section
    level: int = 0
    scales_with_level: bool = True

    # Ability properties
    cost: int = 0
    cost_pool: str | None = None
    duration: str | None = None
    description: str = ""
    is_passive: bool = False
    is_skill: bool = False
    is_spell: bool = False
    target_type: str = "self"

    def is_unlocked(self, character) -> bool:
        return self.unlock_condition(character)

def validate_ability_definition(
    *,
    name: str,
    execute: Callable | None,
    effect_generator: Callable | None,
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
    execute: Callable | None = None,
    effect_generator: Callable | None = None,
    level: int = 0,
    scales_with_level: bool = True,
    cost: int = 0,
    cost_pool: str | None = None,
    duration: str | None = None,
    description: str = "",
    is_passive: bool = False,
    is_skill: bool = False,
    is_spell: bool = False,
    target_type: str = "self",
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
        level=level,
        scales_with_level=scales_with_level,
        cost=cost,
        cost_pool=cost_pool,
        duration=duration,
        description=description,
        is_passive=is_passive,
        is_skill=is_skill,
        is_spell=is_spell,
        target_type=target_type,
    )

    if auto_register:
        from domain.content_registry import register_ability
        register_ability(ability)

    return ability