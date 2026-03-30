from typing import Callable, Dict, Union
from domain.effects import (
    StatIncrease, 
    MultiStatIncrease, 
    CompositeEffect, 
    TargetFilterEffect, 
    ConditionalEffect, 
    ResourceEffect, 
    ScalingEffect, 
    DerivedStatBonus
)

# Optional imports (you may centralize later)
from domain.conditions import *

# CORE PATTERN BUILDERS

def scaled_stat_buff(
    scale_fn: Callable,
    stats: Dict[str, int],
    condition: Callable = None,
):
    effect = ScalingEffect(
        effect_cls=MultiStatIncrease,
        scale_fn=scale_fn,
        stats=stats,
    )

    if condition:
        return TargetFilterEffect(effect, condition=condition)

    return effect

def scaled_resource_effect(
    scale_fn: Callable,
    pool: str,
    condition: Callable = None,
):
    effect = ScalingEffect(
        effect_cls=ResourceEffect,
        scale_fn=scale_fn,
        pool=pool,
    )

    if condition:
        return TargetFilterEffect(effect, condition=condition)

    return effect


def conditional_effect(
    effect,
    condition: Callable,
):
    return ConditionalEffect(
        effect=effect,
        condition=condition,
    )


def composite(*effects):
    return CompositeEffect(list(effects))

def filtered(effect, condition: Callable):
    return TargetFilterEffect(effect, condition=condition)

def apply_tag(tag: str):
    from domain.effects.special import ApplyTagEffect
    return ApplyTagEffect(tag)

def tagged(tag: str):
    return lambda ctx, target: tag in getattr(target, "tags", set())

def on_event(event_name: str, effect, condition=None):
    from domain.effects.special import EventListenerEffect

    return EventListenerEffect(
        event_name=event_name,
        effect=effect,
        condition=condition,
    )

# Skill Check Pattern

def skill_check(
    skill: str,
    stat: str = "intelligence",
    difficulty: Union[int, Callable] = 0,
    on_success=None,
    on_failure=None,
):
    """
    General-purpose skill check wrapper.

    Parameters:
        skill: Name of the skill (e.g. "Distill")
        stat: Attribute used for the roll (default: intelligence)
        difficulty: int OR function(ctx, target) -> int
        on_success: Effect to apply if successful
        on_failure: Optional Effect if failed
    """

    def resolve_difficulty(ctx, target):
        if callable(difficulty):
            return difficulty(ctx, target)
        return difficulty

    def success_condition(ctx, target):
        roll_fn = getattr(ctx.source, f"roll_{stat}")
        roll = roll_fn(skill)
        return roll >= resolve_difficulty(ctx, target)

    # Success branch
    success_effect = ConditionalEffect(
        effect=on_success,
        condition=success_condition,
    )

    if not on_failure:
        return success_effect

    # Failure branch (inverse condition)
    failure_effect = ConditionalEffect(
        effect=on_failure,
        condition=lambda ctx, target: not success_condition(ctx, target),
    )

    from domain.effects import CompositeEffect
    return CompositeEffect([success_effect, failure_effect])

# COMMON ABILITY PATTERNS
# Damage / Heal

def damage(
    scale_fn: Callable,
    condition: Callable = None,
):
    return scaled_resource_effect(
        scale_fn=scale_fn,
        pool="hp",
        condition=condition,
    )

def convert_damage(from_pool: str, to_pool: str):
    from domain.effects.special import ConvertDamageEffect
    return ConvertDamageEffect(from_pool, to_pool)

def heal(
    scale_fn: Callable,
    condition: Callable = None,
):
    return scaled_resource_effect(
        scale_fn=scale_fn,
        pool="hp",
        condition=condition,
    )

# Buffs / Debuffs

def buff(
    scale_fn: Callable,
    stats: Dict[str, int],
    condition: Callable = None,
):
    return scaled_stat_buff(
        scale_fn=scale_fn,
        stats=stats,
        condition=condition,
        )


def debuff(
    scale_fn: Callable,
    stats: Dict[str, int],
    condition: Callable = None,
):
    # negative values expected in stats
    return scaled_stat_buff(
        scale_fn=scale_fn,
        stats=stats,
        condition=condition,
    )

def aura(effect):
    """
    Marks an effect as persistent / area-based.
    Engine can later:
    - enforce one active aura
    - tick per turn/minute
    - handle radius / positioning
    """
    aura_id = aura_id
    effect.aura_id = aura_id
    return effect

def scaled_derived_buff(
    *,
    scale_fn: Callable,
    stat: str,
    condition: Callable = None,
):
    def effect_generator(character):
        amount = scale_fn(character)

        effect = DerivedStatBonus(
            stat=stat,
            amount=int(amount)
        )

        if condition and not condition(character):
            return []

        return [effect]

    return effect_generator

# Conditional (Opposed Rolls, etc.)

def on_success(
    success_condition: Callable,
    effect,
):
    return ConditionalEffect(
        effect=effect,
        condition=success_condition,
    )

def modify_next_attack(modifier_fn):
    from domain.effects.special import ModifyNextAttackEffect
    return ModifyNextAttackEffect(modifier_fn)

def extra_attacks(count: int):
    from domain.effects.special import ExtraAttackEffect
    return ExtraAttackEffect(count)

def passive_modifier(modifier_fn):
    from domain.effects.special import PassiveModifierEffect
    return PassiveModifierEffect(modifier_fn)

def action_override(modifier_fn):
    from domain.effects.special import ActionOverrideEffect
    return ActionOverrideEffect(modifier_fn)

def conditional_damage(scale_fn, condition):
    from domain.effects import ConditionalEffect
    from domain.effects.special import BonusDamageEffect

    return ConditionalEffect(
        effect=BonusDamageEffect(scale_fn),
        condition=condition,
    )
# Multi-Effect Abilities

def multi(*effects):
    return CompositeEffect(list(effects))

# ADVANCED / SPECIAL PATTERNS

def summon(factory_fn, condition: Callable = None):
    from domain.effects.special import CreateEntityEffect

    effect = CreateEntityEffect(factory_fn)

    if condition:
        return TargetFilterEffect(effect, condition)

    return effect


def control(effect, success_condition: Callable):
    return ConditionalEffect(
        effect=effect,
        condition=success_condition,
    )


def inspect(reveal_fn, condition: Callable = None):
    from domain.effects.special import InspectEffect

    effect = InspectEffect(reveal_fn)

    if condition:
        return TargetFilterEffect(effect, condition)

    return effect

def create_item(factory_fn, condition=None):
    from domain.effects.special import CreateItemEffect

    effect = CreateItemEffect(factory_fn)

    if condition:
        from domain.effects import TargetFilterEffect
        return TargetFilterEffect(effect, condition)

    return effect

def apply_state(state_name: str, value_fn=None):
    from domain.effects.special import ApplyStateEffect

    return ApplyStateEffect(state_name, value_fn)
