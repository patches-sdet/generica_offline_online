from collections.abc import Callable

from domain.abilities.compiler_bridge.bonus import compile_bonus_expression
from domain.abilities.compiler_bridge.helpers import require_single_effect
from domain.abilities.definitions.effects_spec import ModifyNextAttackSpec
from domain.abilities.patterns import modify_next_attack


ActiveCompiler = Callable[[object, str, str], Callable]


def _compile_modify_next_attack(effect: ModifyNextAttackSpec, owner_name: str, ability_name: str):
    attack_bonus_fns = [compile_bonus_expression(expr) for expr in effect.attack_bonus]
    damage_bonus_fns = [compile_bonus_expression(expr) for expr in effect.damage_bonus]
    ignore_armor_fns = (
        [compile_bonus_expression(expr) for expr in effect.ignore_armor]
        if isinstance(effect.ignore_armor, tuple)
        else []
    )

    def modifier(ctx, attack):
        source = ctx.source

        if attack_bonus_fns:
            setattr(
                attack,
                "attack_bonus",
                sum(fn(source) for fn in attack_bonus_fns),
            )

        if damage_bonus_fns:
            setattr(
                attack,
                "bonus_damage",
                sum(fn(source) for fn in damage_bonus_fns),
            )

        if isinstance(effect.ignore_armor, tuple):
            setattr(
                attack,
                "ignore_armor",
                sum(fn(source) for fn in ignore_armor_fns),
            )
        elif effect.ignore_armor:
            setattr(attack, "ignore_armor", effect.ignore_armor)

        if effect.ignore_cover:
            setattr(attack, "ignore_cover", True)

        if effect.relative_target_sizes is not None:
            setattr(attack, "minimum_target_size", effect.relative_target_sizes[0])

        if effect.targets_all_adjacent_enemies:
            setattr(attack, "targets_all_adjacent_enemies", True)

        if effect.single_roll_against_all_targets:
            setattr(attack, "single_roll_for_all_targets", True)

    return modify_next_attack(modifier)


_ACTIVE_COMPILERS: dict[type[object], ActiveCompiler] = {
    ModifyNextAttackSpec: _compile_modify_next_attack,
}


def compile_active_effects(effects, owner_name: str, ability_name: str):
    effect = require_single_effect(effects, owner_name, ability_name, "active")
    compiler = _ACTIVE_COMPILERS.get(type(effect))
    if compiler is None:
        raise NotImplementedError(
            f"{owner_name}.{ability_name}: unsupported active effect spec {type(effect).__name__}"
        )

    return compiler(effect, owner_name, ability_name)
