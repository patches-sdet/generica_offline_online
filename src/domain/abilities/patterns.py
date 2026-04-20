from dataclasses import dataclass, replace
from typing import Any, Callable

from domain.effects import (
    CompositeEffect,
    ConditionalEffect,
    DerivedStatBonus,
    Damage,
    Heal,
    MultiStatIncrease,
    ScalingEffect,
    TargetFilterEffect,
)
from domain.effects.base import Effect, EffectContext
from domain.effects.special.damage import TransferEffect

# ---------------------------------------------------------------------------
# Pattern helper contract notes
#
# Most helpers in this module return Effect instances (or wrapped/composed
# Effect instances).
#
# The main intentional exception is scaled_derived_buff(), which returns a
# ctx-based effect generator:
#
#     Callable[[EffectContext], list[Effect]]
#
# This is preserved to match the current passive-ability builder contract.
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class DifficultyTable:
    values: dict[str, int]

    def get(self, key: str) -> int:
        if key not in self.values:
            raise ValueError(f"Unknown difficulty tier: {key}")
        return self.values[key]

    def __getitem__(self, key: str) -> int:
        return self.get(key)

def difficulty_from_table(
    table: DifficultyTable,
    metadata_key: str = "tier",
) -> Callable[[EffectContext, Any], int]:
    def resolve(ctx: EffectContext, target: Any) -> int:
        key = ctx.metadata.get(metadata_key)
        if key is None:
            raise ValueError(f"Missing required metadata key: {metadata_key}")
        return table[key]

    return resolve

# Internal Helpers

def _with_optional_filter(
    effect: Effect,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return TargetFilterEffect(effect, condition=condition) if condition else effect

def _scaled_multi_increase(
    *,
    scale_fn: Callable[[Any], int],
    payload_key: str,
    payload: dict[str, int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    effect = ScalingEffect(
        effect_cls=MultiStatIncrease,
        scale_fn=scale_fn,
        effect_kwargs={payload_key: payload},
    )
    return _with_optional_filter(effect, condition)

def _scaled_resource_effect(
    *,
    effect_cls: type[Effect],
    scale_fn: Callable[[Any], int],
    pool: str,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    effect = ScalingEffect(
        effect_cls=effect_cls,
        scale_fn=scale_fn,
        effect_kwargs={"pool": pool},
    )
    return _with_optional_filter(effect, condition)

# General Composition / Filtering

def conditional_effect(
    effect: Effect,
    condition: Callable[[EffectContext, Any], bool],
) -> Effect:
    return ConditionalEffect(effect=effect, condition=condition)

def composite(*effects: Effect) -> Effect:
    return CompositeEffect(list(effects))

def filtered(
    effect: Effect,
    condition: Callable[[EffectContext, Any], bool],
) -> Effect:
    return TargetFilterEffect(effect, condition=condition)

def tagged(tag: str) -> Callable[[EffectContext, Any], bool]:
    def predicate(ctx: EffectContext, target: Any) -> bool:
        return tag in getattr(target, "tags", set())

    return predicate

def on_event(
    event_name: str,
    effect: Effect,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    from domain.effects.special.event import EventListenerEffect

    return EventListenerEffect(
        event_name=event_name,
        effect=effect,
        condition=condition,
    )


def on_success(
    success_condition: Callable[[EffectContext, Any], bool],
    effect: Effect,
) -> Effect:
    return ConditionalEffect(effect=effect, condition=success_condition)

# Stat / Skill / Resource / Derived Patterns

def scaled_stat_buff(
    scale_fn: Callable[[Any], int],
    stats: dict[str, int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return _scaled_multi_increase(
        scale_fn=scale_fn,
        payload_key="stats",
        payload=stats,
        condition=condition,
    )

def scaled_skill_buff(
    scale_fn: Callable[[Any], int],
    skills: dict[str, int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return _scaled_multi_increase(
        scale_fn=scale_fn,
        payload_key="skills",
        payload=skills,
        condition=condition,
    )

def scaled_resource_effect(
    effect_cls: type[Effect],
    scale_fn: Callable[[Any], int],
    pool: str,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return _scaled_resource_effect(
        effect_cls=effect_cls,
        scale_fn=scale_fn,
        pool=pool,
        condition=condition,
    )

def scaled_derived_buff(
    *,
    scale_fn: Callable[[Any], int],
    stat: str,
    condition: Callable[[Any], bool] | None = None,
) -> Callable[[EffectContext], list[Effect]]:
    """
    Intentionally returns a ctx-based effect generator rather than an Effect
    instance, because the current passive-ability builder expects a function
    of shape:

        Callable[[EffectContext], list[Effect]]
    """
    def effect_generator(ctx: EffectContext) -> list[Effect]:
        if condition and not condition(ctx.source):
            return []

        amount = scale_fn(ctx.source)
        return [DerivedStatBonus(stat=stat, amount=int(amount))]

    return effect_generator

def skill_check(
    ability: str,
    stat: str = "intelligence",
    difficulty: int | Callable[[EffectContext, Any], int] = 0,
    on_success: Effect | None = None,
    on_failure: Effect | None = None,
) -> Effect:
    def resolve_difficulty(ctx: EffectContext, target: Any) -> int:
        return difficulty(ctx, target) if callable(difficulty) else difficulty

    def success_condition(ctx: EffectContext, target: Any) -> bool:
        roll_fn = getattr(ctx.source, f"roll_{stat}", None)
        if roll_fn is None:
            raise AttributeError(
                f"{type(ctx.source).__name__} has no roll_{stat}() method"
            )
        roll = roll_fn(ability)
        return roll >= resolve_difficulty(ctx, target)

    success_effect = ConditionalEffect(
        effect=on_success,
        condition=success_condition,
    )

    if not on_failure:
        return success_effect

    failure_effect = ConditionalEffect(
        effect=on_failure,
        condition=lambda ctx, target: not success_condition(ctx, target),
    )

    return CompositeEffect([success_effect, failure_effect])

# Damage / Healing Helpers

def hp_damage(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="hp",
        condition=condition,
    )

def sanity_damage(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="sanity",
        condition=condition,
    )

def moxie_damage(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="moxie",
        condition=condition,
    )

def stamina_damage(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="stamina",
        condition=condition,
    )

def fortune_damage(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="fortune",
        condition=condition,
    )

def heal_hp(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="hp",
        condition=condition,
    )

def heal_sanity(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="sanity",
        condition=condition,
    )

def heal_stamina(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="stamina",
        condition=condition,
    )

def heal_moxie(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="moxie",
        condition=condition,
    )

def heal_fortune(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="fortune",
        condition=condition,
    )

def conditional_damage(
    scale_fn: Callable[[Any], int],
    condition: Callable[[EffectContext, Any], bool],
) -> Effect:
    from domain.effects.special.damage import BonusDamageEffect

    return ConditionalEffect(
        effect=BonusDamageEffect(scale_fn),
        condition=condition,
    )

def transfer_stat(
    amount_fn: Callable,
    condition: Callable | None = None,
) -> Effect:
    return TransferEffect(amount_fn=amount_fn, condition=condition)

# Special Effect Constructors

def apply_tag(tag: str) -> Effect:
    from domain.effects.special.tag import ApplyTagEffect

    return ApplyTagEffect(tag)

def apply_state(
    state_name: str,
    value_fn: Callable | None = None,
) -> Effect:
    from domain.effects.special.state import ApplyStateEffect

    return ApplyStateEffect(state_name, value_fn)

def aura(effect: Effect, aura_id: str | None = None) -> Effect:
    if aura_id is None:
        aura_id = f"aura:{id(effect)}"
    return replace(effect, aura_id=aura_id)

def modify_next_attack(modifier_fn: Callable) -> Effect:
    """
    modifier_fn should accept: (ctx, attack)
    """
    from domain.effects.special.attack import ModifyNextAttackEffect

    return ModifyNextAttackEffect(modifier_fn)

def extra_attacks(count: int) -> Effect:
    from domain.effects.special.action import ExtraAttackEffect

    return ExtraAttackEffect(count)

def passive_modifier(modifier_fn: Callable) -> Effect:
    """
    modifier_fn should accept: (ctx)
    """
    from domain.effects.special.action import PassiveModifierEffect

    return PassiveModifierEffect(modifier_fn)

def action_override(modifier_fn: Callable) -> Effect:
    """
    modifier_fn should accept: (ctx)
    """
    from domain.effects.special.action import ActionOverrideEffect

    return ActionOverrideEffect(modifier_fn)

def summon(
    factory_fn: Callable,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    from domain.effects.special.crafting import CreateEntityEffect

    return _with_optional_filter(CreateEntityEffect(factory_fn), condition)

def inspect(
    reveal_fn: Callable,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    from domain.effects.special.action import InspectEffect

    return _with_optional_filter(InspectEffect(reveal_fn), condition)

def create_item(
    factory_fn: Callable,
    condition: Callable[[EffectContext, Any], bool] | None = None,
) -> Effect:
    from domain.effects.special.crafting import CreateItemEffect

    return _with_optional_filter(CreateItemEffect(factory_fn), condition)