from .base import Effect, EffectContext
from .scaling import ScalingEffect
from .stat_effects import StatIncrease, MultiStatIncrease, DerivedStatBonus, DerivedStatOverride
from .resource_effects import ResourceEffect, Heal, Damage, SpendResource
from .special.action import ExtraAttackEffect, ActionOverrideEffect
from .special.attack import ModifyNextAttackEffect
from .special.crafting import CreateItemEffect
from .special.damage import BonusDamageEffect
from .special.event import EventListenerEffect
from .special.state import ApplyStateEffect 
from .special.tag import ApplyTagEffect

# Conditional / wrappers
from .conditional import ConditionalEffect, CompositeEffect

from .targeting import TargetFilterEffect


__all__ = [
    # Base
    "Effect",
    "EffectContext",

    # Stat effects
    "StatIncrease",
    "MultiStatIncrease",
    "DerivedStatBonus",
    "DerivedStatOverride",

    # Resource
    "Heal",
    "Damage",
    "SpendResource",
    "ResourceEffect",

    # Special / utility
    "AttackEffect",
    "MultiAttackEffect",
    "CraftingEffect",
    "ExtraAttackEffect",
    "ActionOverrideEffect",
    "BonusDamageEffect",
    "CreateEntityEffect",
    "ApplyStateEffect",
    "RemoveStateEffect",
    "AddTagEffect",
    "RemoveTagEffect",

    # Conditional
    "ConditionalEffect",
    "CompositeEffect",
    "TargetFilterEffect",
]
