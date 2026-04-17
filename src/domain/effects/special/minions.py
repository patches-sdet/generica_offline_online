from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from domain.effects.base import Effect, EffectContext


ATTRIBUTE_LIST: tuple[str, ...] = (
    "strength",
    "constitution",
    "dexterity",
    "agility",
    "intelligence",
    "wisdom",
    "willpower",
    "perception",
    "charisma",
    "luck",
)


def _ensure_target_tags(target) -> set[str]:
    tags = getattr(target, "tags", None)
    if tags is None:
        tags = set()
        setattr(target, "tags", tags)
    return tags


def _ensure_target_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _get_target_stat_value(target, stat: str) -> int:
    if hasattr(target, "get_stat"):
        return int(target.get_stat(stat, 0))

    attrs = getattr(target, "attributes", None)
    if attrs is None:
        return 0

    if isinstance(attrs, dict):
        return int(attrs.get(stat, 0))

    return int(getattr(attrs, stat, 0))


def _get_target_skill_value(target, skill_name: str) -> int:
    if hasattr(target, "get_skill_level"):
        return int(target.get_skill_level(skill_name, 0))

    skill_levels = getattr(target, "skill_levels", None)
    if skill_levels is None:
        return 0

    return int(skill_levels.get(skill_name, 0))


def _ensure_target_skill_levels(target) -> dict[str, int]:
    skill_levels = getattr(target, "skill_levels", None)
    if skill_levels is None:
        skill_levels = {}
        setattr(target, "skill_levels", skill_levels)
    return skill_levels


@dataclass(slots=True)
class ApplyAffiliationTagEffect(Effect):
    """
    Apply an affiliation tag to matching targets.

    Optional state payload is useful for recording controller/source metadata,
    duration hints, or other runtime hooks.
    """

    tag: str
    condition: Callable[[EffectContext, object], bool] | None = None
    state_key: str | None = None
    state_value_fn: Callable[[EffectContext, object], object] | None = None

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if self.condition is not None and not self.condition(context, target):
                continue

            tags = _ensure_target_tags(target)
            tags.add(self.tag)

            if self.state_key is not None:
                states = _ensure_target_states(target)
                states[self.state_key] = (
                    self.state_value_fn(context, target)
                    if self.state_value_fn is not None
                    else True
                )


@dataclass(slots=True)
class RemoveAffiliationTagEffect(Effect):
    """
    Remove an affiliation tag from matching targets.
    """

    tag: str
    condition: Callable[[EffectContext, object], bool] | None = None
    clear_state_keys: tuple[str, ...] = ()

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if self.condition is not None and not self.condition(context, target):
                continue

            tags = _ensure_target_tags(target)
            tags.discard(self.tag)

            if self.clear_state_keys:
                states = _ensure_target_states(target)
                for key in self.clear_state_keys:
                    states.pop(key, None)


@dataclass(slots=True)
class ScaledNonZeroAttributeBuffEffect(Effect):
    """
    Add a scaled bonus to each non-zero attribute on matching targets.

    This is the exact reusable primitive for things like Creator's Guardians.
    """

    scale_fn: Callable[[object], int]
    condition: Callable[[EffectContext, object], bool]
    stats: tuple[str, ...] = ATTRIBUTE_LIST
    source_name: str = "Scaled Non-Zero Attribute Buff"

    def apply(self, context: EffectContext) -> None:
        amount = int(self.scale_fn(context.source))
        if amount <= 0:
            return

        for target in context.targets:
            if not self.condition(context, target):
                continue

            for stat in self.stats:
                current = _get_target_stat_value(target, stat)
                if current != 0:
                    target.add_stat(stat, amount, source=self.source_name)


@dataclass(slots=True)
class ScaledAttributeBuffEffect(Effect):
    """
    Add a scaled bonus to the listed attributes on matching targets,
    regardless of whether the current value is zero.
    """

    scale_fn: Callable[[object], int]
    stats: tuple[str, ...]
    condition: Callable[[EffectContext, object], bool]
    source_name: str = "Scaled Attribute Buff"

    def apply(self, context: EffectContext) -> None:
        amount = int(self.scale_fn(context.source))
        if amount <= 0:
            return

        for target in context.targets:
            if not self.condition(context, target):
                continue

            for stat in self.stats:
                target.add_stat(stat, amount, source=self.source_name)


@dataclass(slots=True)
class ScaledDerivedStatBuffEffect(Effect):
    """
    Add a scaled derived-stat bonus to matching targets.

    Works with your current derived bonus accumulation model.
    """

    scale_fn: Callable[[object], int]
    stat: str
    condition: Callable[[EffectContext, object], bool]
    source_name: str = "Scaled Derived Buff"

    def apply(self, context: EffectContext) -> None:
        amount = int(self.scale_fn(context.source))
        if amount == 0:
            return

        for target in context.targets:
            if not self.condition(context, target):
                continue

            target._derived_bonuses[self.stat] += amount


@dataclass(slots=True)
class ScaledSkillBuffEffect(Effect):
    """
    Add a scaled bonus to listed skills on matching targets.

    Useful for pet/minion training or group specialization effects.
    """

    scale_fn: Callable[[object], int]
    skills: tuple[str, ...]
    condition: Callable[[EffectContext, object], bool]

    def apply(self, context: EffectContext) -> None:
        amount = int(self.scale_fn(context.source))
        if amount == 0:
            return

        for target in context.targets:
            if not self.condition(context, target):
                continue

            skill_levels = _ensure_target_skill_levels(target)
            for skill_name in self.skills:
                skill_levels[skill_name] = skill_levels.get(skill_name, 0) + amount


@dataclass(slots=True)
class ScaledNonZeroSkillBuffEffect(Effect):
    """
    Add a scaled bonus only to skills the target already has above zero.
    """

    scale_fn: Callable[[object], int]
    skills: tuple[str, ...]
    condition: Callable[[EffectContext, object], bool]

    def apply(self, context: EffectContext) -> None:
        amount = int(self.scale_fn(context.source))
        if amount == 0:
            return

        for target in context.targets:
            if not self.condition(context, target):
                continue

            skill_levels = _ensure_target_skill_levels(target)
            for skill_name in self.skills:
                if _get_target_skill_value(target, skill_name) > 0:
                    skill_levels[skill_name] = skill_levels.get(skill_name, 0) + amount


@dataclass(slots=True)
class ScaledResourceBuffEffect(Effect):
    """
    Add a scaled amount directly to a resource pool on matching targets.

    This uses modify_resource(), so it affects current value, not max value.
    If you later want max-pool support, make a separate effect.
    """

    scale_fn: Callable[[object], int]
    pool: str
    condition: Callable[[EffectContext, object], bool]

    def apply(self, context: EffectContext) -> None:
        amount = int(self.scale_fn(context.source))
        if amount == 0:
            return

        for target in context.targets:
            if not self.condition(context, target):
                continue

            target.modify_resource(self.pool, amount)


@dataclass(slots=True)
class GrantControlledGroupMembershipEffect(Effect):
    """
    Higher-level convenience effect:
    - applies a tag
    - records controller/source metadata
    - optionally records duration metadata

    Good for recruitment / taming / binding / marking skills.
    """

    tag: str
    condition: Callable[[EffectContext, object], bool]
    controller_state_key: str = "controller"
    duration_state_key: str | None = None
    duration_fn: Callable[[EffectContext, object], object] | None = None
    extra_state: dict[str, object] = field(default_factory=dict)

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if not self.condition(context, target):
                continue

            tags = _ensure_target_tags(target)
            tags.add(self.tag)

            states = _ensure_target_states(target)
            states[self.controller_state_key] = context.source

            if self.duration_state_key is not None:
                states[self.duration_state_key] = (
                    self.duration_fn(context, target)
                    if self.duration_fn is not None
                    else True
                )

            for key, value in self.extra_state.items():
                states[key] = value