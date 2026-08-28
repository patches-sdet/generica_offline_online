from collections.abc import Callable

from domain.abilities.compiler_bridge.bonus import compile_bonus_expression
from domain.abilities.compiler_bridge.helpers import require_single_effect
from domain.abilities.definitions.effects_spec import DerivedStatBuffSpec
from domain.abilities.patterns import scaled_derived_buff


PassiveCompiler = Callable[[object, str, str], Callable]


def _compile_derived_stat_buff(effect: DerivedStatBuffSpec, owner_name: str, ability_name: str):
    if not effect.stat:
        raise ValueError(f"{owner_name}.{ability_name}: DerivedStatBuffSpec requires a stat")

    if len(effect.amount) != 1:
        raise NotImplementedError(
            f"{owner_name}.{ability_name}: expected exactly one amount expression for now"
        )

    scale_fn = compile_bonus_expression(effect.amount[0])
    return scaled_derived_buff(
        scale_fn=scale_fn,
        stat=effect.stat,
    )


_PASSIVE_COMPILERS: dict[type[object], PassiveCompiler] = {
    DerivedStatBuffSpec: _compile_derived_stat_buff,
}


def compile_passive_effects(effects, owner_name: str, ability_name: str):
    effect = require_single_effect(effects, owner_name, ability_name, "passive")
    compiler = _PASSIVE_COMPILERS.get(type(effect))
    if compiler is None:
        raise NotImplementedError(
            f"{owner_name}.{ability_name}: unsupported passive effect spec {type(effect).__name__}"
        )

    return compiler(effect, owner_name, ability_name)
