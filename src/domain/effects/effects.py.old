from typing import Dict, Callable, List, Optional

# CONTEXT

class EffectContext:
    """
    Carries all runtime information needed to apply effects.
    """

    def __init__(self, source, targets: List):
        self.source = source
        self.targets = targets

# BASE EFFECT CLASS

class Effect:
    """
    Base class for all effects.

    Rules:
    - Effects operate on targets via EffectContext
    - Effects NEVER mutate outside Character APIs
    - Target filtering happens via applies_to()
    """

    priority = 0  # future ordering system

    def apply(self, context: EffectContext):
        for target in context.targets:
            if not self.applies_to(context, target):
                continue
            self._apply_to_target(context, target)

    def applies_to(self, context: EffectContext, target) -> bool:
        return True

    def _apply_to_target(self, context: EffectContext, target):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()

# ATTRIBUTE EFFECTS

class StatIncrease(Effect):
    """
    Increase a single attribute.
    """

    def __init__(self, stat: str, amount: int, source=None):
        self.stat = stat
        self.amount = amount
        self.source = source

    def _apply_to_target(self, context, target):
        if not hasattr(target.attributes, self.stat):
            raise ValueError(f"Invalid attribute: {self.stat}")

        target.add_attribute(self.stat, self.amount, source=self.source)

    def to_dict(self):
        return {
            "type": "stat_increase",
            "stat": self.stat,
            "amount": self.amount,
        }


class MultiStatIncrease(Effect):
    """
    Increase multiple attributes at once.
    """

    def __init__(self, stats: Dict[str, int], source=None):
        self.stats = stats
        self.source = source

    def _apply_to_target(self, context, target):
        for stat, amount in self.stats.items():
            if not hasattr(target.attributes, stat):
                raise ValueError(f"Invalid attribute: {stat}")

            target.add_attribute(stat, amount, source=self.source)

    def to_dict(self):
        return {
            "type": "multi_stat_increase",
            "stats": self.stats,
        }

# CONDITIONAL / TARGETING

class ConditionalEffect(Effect):
    """
    Wraps another effect with a condition.
    """

    def __init__(self, effect: Effect, condition: Callable):
        self.effect = effect
        self.condition = condition

    def applies_to(self, context, target):
        return self.condition(context, target)

    def _apply_to_target(self, context, target):
        self.effect._apply_to_target(context, target)


class TargetFilterEffect(Effect):
    """
    Filters targets BEFORE applying inner effect.
    """

    def __init__(self, effect: Effect, condition: Callable):
        self.effect = effect
        self.condition = condition

    def apply(self, context: EffectContext):
        filtered_targets = [
            t for t in context.targets if self.condition(context, t)
        ]
        new_context = EffectContext(context.source, filtered_targets)
        self.effect.apply(new_context)

class ControlEffect:
    def __init__(self, duration="instant"):
        self.duration = duration

    def apply(self, context):
        for target in context.targets:
            target.controller = context.source

# RESOURCE EFFECTS

class ResourceEffect(Effect):
    """
    Modifies a resource pool (hp, stamina, etc.)
    Positive = heal, Negative = damage
    """

    def __init__(self, pool: str, amount: int, source=None):
        self.pool = pool
        self.amount = amount
        self.source = source

    def _apply_to_target(self, context, target):
        if self.amount >= 0:
            target.runtime.heal(self.pool, self.amount)
        else:
            target.runtime.damage(self.pool, -self.amount)

# STATUS EFFECTS

class ApplyStatusEffect(Effect):
    """
    Applies a named status effect.
    """

    def __init__(self, status: str, duration: Optional[int] = None, source=None):
        self.status = status
        self.duration = duration
        self.source = source

    def _apply_to_target(self, context, target):
        target.add_status(self.status, self.duration, source=self.source)

class InspectEffect:
    def __init__(self, reveal_fn):
        self.reveal_fn = reveal_fn

    def apply(self, context):
        for target in context.targets:
            info = self.reveal_fn(context.source, target)
            # send to UI/log system

# SCALING / COMPOSITION

class ScalingEffect(Effect):
    """
    Dynamically computes amount, then applies inner effect.
    """

    def __init__(self, effect_cls, scale_fn: Callable, **kwargs):
        self.effect_cls = effect_cls
        self.scale_fn = scale_fn
        self.kwargs = kwargs

    def apply(self, context: EffectContext):
        amount = self.scale_fn(context.source)
        effect = self.effect_cls(amount=amount, **self.kwargs)
        effect.apply(context)


class CompositeEffect(Effect):
    """
    Combines multiple effects.
    """

    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def apply(self, context: EffectContext):
        for effect in self.effects:
            effect.apply(context)

# DERIVED STATS

class DerivedStatBonus(Effect):
    """
    Adds to derived stats (hp, armor, etc.)
    """

    VALID_STATS = {
        "hp", "sanity", "stamina", "moxie", "fortune",
        "armor", "mental_fortitude", "endurance", "cool", "fate"
    }

    def __init__(self, stat: str, amount: int, source=None):
        if stat not in self.VALID_STATS:
            raise ValueError(f"Invalid derived stat: {stat}")

        self.stat = stat
        self.amount = amount
        self.source = source

    def _apply_to_target(self, context, target):
        target._derived_bonuses[self.stat] = (
            target._derived_bonuses.get(self.stat, 0) + self.amount
        )

        if hasattr(target, "_derived_sources"):
            target._derived_sources[self.stat][self.source] += self.amount

    def to_dict(self):
        return {
            "type": "derived_stat_bonus",
            "stat": self.stat,
            "amount": self.amount,
        }


class DerivedStatOverride(Effect):
    """
    Overrides a derived stat completely.
    """

    def __init__(self, stat: str, amount: int, source=None):
        self.stat = stat
        self.amount = amount
        self.source = source
        self.priority = 100

    def _apply_to_target(self, context, target):
        if target._derived_overrides is None:
            target._derived_overrides = {}

        target._derived_overrides[self.stat] = self.amount

    def to_dict(self):
        return {
            "type": "derived_stat_override",
            "stat": self.stat,
            "amount": self.amount,
        }

# CREATION EFFECTS

class CreateEntityEffect:
    def __init__(self, factory_fn):
        self.factory_fn = factory_fn

    def apply(self, context):
        for target in context.targets:
            entity = self.factory_fn(context.source, target)
            # attach to world / party / registry

# HELPERS

def make_effects(**mods):
    """
    Convenience helper for simple stat increases.
    """
    return [StatIncrease(stat, amount) for stat, amount in mods.items()]
