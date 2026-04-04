from typing import Callable, Dict, Union
from dataclasses import dataclass
from domain.effects import (
    MultiStatIncrease,
    CompositeEffect,
    TargetFilterEffect,
    ConditionalEffect,
    ResourceEffect,
    ScalingEffect,
    DerivedStatBonus,
    EventListenerEffect,
)
from domain.effects import Damage, Heal
from domain.effects.special.damage import TransferEffect
from domain.conditions import *
from domain.effects.base import Effect

@dataclass(slots=True)
class DifficultyTable:
    values: dict[str, int]

    def get(self, key: str) -> int:
        if key not in self.values:
            raise ValueError(f"Unknown difficulty tier: {key}")
        return self.values[key]

    def __getitem__(self, key: str) -> int:
        return self.get(key)

@dataclass(slots=True)
class ApplyChallengedEffect(Effect):
    def __init__(self, challenger, penalty, duration):
        self.challenger = challenger
        self.penalty = penalty
        self.duration = duration

    def apply(self, context):
        for target in context.targets:
            target.states["challenged"] = {
                "challenger": self.challenger,
                "penalty": self.penalty,
                "duration": self.duration,
            }

def difficulty_from_table(table: DifficultyTable, metadata_key: str = "tier"):
    def resolve(ctx, target):
        key = ctx.metadata.get(metadata_key)
        if key is None:
            raise ValueError(f"Missing required metadata key: {metadata_key}")
        return table[key]
    return resolve

def scaled_stat_buff(
    scale_fn: Callable,
    stats: dict[str, int],
    condition: Callable = None,
):
    effect = ScalingEffect(
        effect_cls=MultiStatIncrease,
        scale_fn=scale_fn,
        effect_kwargs={"stats": stats},
    )

    if condition:
        return TargetFilterEffect(effect, condition=condition)

    return effect

def scaled_resource_effect(
    effect_cls,
    scale_fn: Callable,
    pool: str,
    condition: Callable = None,
):
    effect = ScalingEffect(
        effect_cls=effect_cls,
        scale_fn=scale_fn,
        effect_kwargs={"pool": pool},
    )

    if condition:
        return TargetFilterEffect(effect, condition=condition)

    return effect

def conditional_effect(effect, condition: Callable):
    return ConditionalEffect(effect=effect, condition=condition)

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

def skill_check(
    ability: str,
    stat: str = "intelligence",
    difficulty: Union[int, Callable] = 0,
    on_success=None,
    on_failure=None,
):
    def resolve_difficulty(ctx, target):
        return difficulty(ctx, target) if callable(difficulty) else difficulty

    def success_condition(ctx, target):
        roll_fn = getattr(ctx.source, f"roll_{stat}")
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

def damage(scale_fn: Callable, condition: Callable = None):
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="hp",
        condition=condition,
    )

def heal(scale_fn: Callable, condition: Callable = None):
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="hp",
        condition=condition,
    )

def transfer_stat(amount_fn, condition=None):
    return TransferEffect(amount_fn=amount_fn, condition=condition)

def buff(
    scale_fn: Callable,
    stats: Dict[str, int],
    condition: Callable = None,
):
    return scaled_stat_buff(scale_fn=scale_fn, stats=stats, condition=condition)

def debuff(
    scale_fn: Callable,
    stats: Dict[str, int],
    condition: Callable = None,
):
    return scaled_stat_buff(scale_fn=scale_fn, stats=stats, condition=condition)

def aura(effect, aura_id: str | None = None):
    if aura_id is None:
        aura_id = f"aura:{id(effect)}"
    effect.aura_id = aura_id
    return effect

def scaled_derived_buff(
    *,
    scale_fn: Callable,
    stat: str,
    condition: Callable = None,
):
    def effect_generator(character):
        if condition and not condition(character):
            return []

        amount = scale_fn(character)
        return [DerivedStatBonus(stat=stat, amount=int(amount))]

    return effect_generator

def on_success(success_condition: Callable, effect):
    return ConditionalEffect(effect=effect, condition=success_condition)

def modify_next_attack(modifier_fn):
    """
    modifier_fn should accept: (ctx, attack)
    """
    from domain.effects.special import ModifyNextAttackEffect
    return ModifyNextAttackEffect(modifier_fn)

def extra_attacks(count: int):
    from domain.effects.special import ExtraAttackEffect
    return ExtraAttackEffect(count)

def passive_modifier(modifier_fn):
    """
    modifier_fn should accept: (ctx)
    """
    from domain.effects.special import PassiveModifierEffect
    return PassiveModifierEffect(modifier_fn)

def action_override(modifier_fn):
    """
    modifier_fn should accept: (ctx)
    """
    from domain.effects.special import ActionOverrideEffect
    return ActionOverrideEffect(modifier_fn)

def conditional_damage(scale_fn, condition):
    from domain.effects.special import BonusDamageEffect
    return ConditionalEffect(
        effect=BonusDamageEffect(scale_fn),
        condition=condition,
    )

def summon(factory_fn, condition: Callable = None):
    from domain.effects.special import CreateEntityEffect
    effect = CreateEntityEffect(factory_fn)
    return TargetFilterEffect(effect, condition) if condition else effect

def control(effect, success_condition: Callable):
    return ConditionalEffect(effect=effect, condition=success_condition)

def inspect(reveal_fn, condition: Callable = None):
    from domain.effects.special import InspectEffect
    effect = InspectEffect(reveal_fn)
    return TargetFilterEffect(effect, condition) if condition else effect

def create_item(factory_fn, condition=None):
    from domain.effects.special import CreateItemEffect
    effect = CreateItemEffect(factory_fn)
    return TargetFilterEffect(effect, condition) if condition else effect

def apply_state(state_name: str, value_fn=None):
    from domain.effects.special import ApplyStateEffect
    return ApplyStateEffect(state_name, value_fn)