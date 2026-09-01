from collections.abc import Callable

from domain.abilities.definitions.effects_spec import (
    AbilityLevelBonus,
    FlatBonus,
    ProgressionLevelBonus,
)


BonusCompiler = Callable[[object], Callable]


def _compile_flat_bonus(expr: FlatBonus):
    return lambda source, e=expr: e.amount


def _compile_ability_level_bonus(expr: AbilityLevelBonus):
    return lambda source, e=expr: source.get_ability_effective_level(e.ability_name) * e.multiplier


def _compile_progression_level_bonus(expr: ProgressionLevelBonus):
    return lambda source, e=expr: source.get_progression_level(
        e.source_type,
        e.source_name,
        0,
    ) * e.multiplier


_BONUS_COMPILERS: dict[type[object], BonusCompiler] = {
    FlatBonus: _compile_flat_bonus,
    AbilityLevelBonus: _compile_ability_level_bonus,
    ProgressionLevelBonus: _compile_progression_level_bonus,
}


def compile_bonus_expression(expr):
    compiler = _BONUS_COMPILERS.get(type(expr))
    if compiler is None:
        raise NotImplementedError(f"Unsupported bonus expression: {type(expr).__name__}")

    return compiler(expr)
