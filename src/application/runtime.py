from __future__ import annotations

import logging

from application.events import emit_event
from application.targeting import resolve_targets
from domain.attributes import ATTRIBUTE_NAMES
from domain.calculations import recalculate
from domain.content_registry import get_ability
from domain.effects import SpendResource
from domain.effects.base import EffectContext
from domain.skill_ownership import (
    add_skill_levels,
    has_skill,
)
from observability import context_snapshot, describe_exception, entity_id, log_trace


LOGGER = logging.getLogger(__name__)


def prompt_for_variable_cost(ability) -> int:
    pool_name = ability.cost_pool or "fortune"

    while True:
        raw = input(f"Enter {pool_name} to spend for {ability.name}: ").strip()

        if not raw.isdigit():
            print("Please enter a non-negative whole number.")
            continue

        return int(raw)

def award_generic_skill(
    character,
    skill_name: str,
    source: str = "runtime:first_use",
    levels: int = 1,
) -> bool:
    """
    Award a generic skill the first time it is successfully used.
    Returns True if the skill was newly awarded.
    """
    if character.has_skill(skill_name):
        return False

    add_skill_levels(character, skill_name, source=source, levels=levels)
    recalculate(character)
    return True

def award_attribute_from_runtime_use(
    character,
    stat: str,
    amount: int = 1,
    source: str = "runtime:experience_die",
) -> None:
    """
    Permanent attribute increase earned through successful play.
    This survives rebuild because it writes to canonical character storage.
    """
    if stat not in ATTRIBUTE_NAMES:
        raise ValueError(f"Unknown attribute for runtime increase: {stat!r}")
    if amount <= 0:
        raise ValueError(f"Runtime attribute increase must be positive: {stat} -> {amount}")

    character.add_manual_attribute_increase(stat, amount, source=source)
    recalculate(character)

def award_skill_from_runtime_use(
    character,
    skill_name: str,
    amount: int = 1,
    source: str = "runtime:experience_die",
) -> None:
    if amount <= 0:
        raise ValueError(f"Runtime skill increase must be positive: {skill_name} -> {amount}")

    add_skill_levels(character, skill_name, source=source, levels=amount)
    recalculate(character)

def apply_damage(
    character,
    *,
    pool: str,
    amount: int,
    source: str = "runtime:damage",
) -> dict[str, int | str]:
    """
    Apply direct runtime damage to a resource pool.

    Current runtime support is intentionally conservative and only implements
    the concrete behavior needed by tests and the documented restart flow.
    In particular, HP damage can trigger the Toughness rank-up rule when a
    single hit exceeds Constitution + current Toughness rank.
    """
    if amount <= 0:
        raise ValueError(f"Damage amount must be positive: {amount}")

    before = getattr(character, f"current_{pool}")
    success = character.modify_resource(pool, -amount)
    if success is False:
        raise ValueError(f"Not enough {pool} to take {amount} damage")

    toughness_rank_up = 0
    if pool == "hp":
        current_toughness = character.get_skill_level("Toughness", 0)
        threshold = character.get_stat("constitution") + current_toughness
        if amount > threshold:
            award_skill_from_runtime_use(
                character,
                "Toughness",
                amount=1,
                source="runtime:toughness_damage",
            )
            toughness_rank_up = 1

    return {
        "pool": pool,
        "amount": amount,
        "before": before,
        "after": getattr(character, f"current_{pool}"),
        "source": source,
        "toughness_rank_up": toughness_rank_up,
    }

def award_experience_die_result(
    character,
    *,
    stat: str,
    skill_name: str | None = None,
    experience_die: int,
) -> dict[str, int]:
    """
    Apply the permanent gain outcome from the experience die.

    Rules implemented:
    - attribute-only roll:
        if experience_die * 10 > current attribute, gain +1 attribute
        a 9 always grants +1 attribute
    - skill roll:
        if experience_die * 10 > current skill, gain +1 skill
        a 9 grants +1 skill and +1 linked attribute

    Returns a simple summary of what was awarded.
    """
    if stat not in ATTRIBUTE_NAMES:
        raise ValueError(f"Unknown attribute for experience die award: {stat!r}")
    if not 0 <= experience_die <= 9:
        raise ValueError(f"Experience die must be between 0 and 9 inclusive: {experience_die}")

    awarded = {
        "attribute_increase": 0,
        "skill_increase": 0,
    }

    threshold = experience_die * 10

    if skill_name:
        current_skill = character.get_skill_level(skill_name, 0)

        if experience_die == 9:
            award_skill_from_runtime_use(
                character,
                skill_name,
                amount=1,
                source="runtime:experience_die",
            )
            award_attribute_from_runtime_use(
                character,
                stat,
                amount=1,
                source="runtime:experience_die",
            )
            awarded["skill_increase"] = 1
            awarded["attribute_increase"] = 1
            return awarded

        if threshold > current_skill:
            award_skill_from_runtime_use(
                character,
                skill_name,
                amount=1,
                source="runtime:experience_die",
            )
            awarded["skill_increase"] = 1

        return awarded

    current_attr = character.get_stat(stat)

    if experience_die == 9 or threshold > current_attr:
        award_attribute_from_runtime_use(
            character,
            stat,
            amount=1,
            source="runtime:experience_die",
        )
        awarded["attribute_increase"] = 1

    return awarded

def prompt_for_context_options(ability) -> dict:
    metadata = {}

    if getattr(ability, "requires_chosen_stat", False):
        metadata["chosen_stat"] = input("Choose a stat: ").strip().lower()

    return metadata

def apply_effects(effects, context: EffectContext):
    if not effects:
        log_trace(
            LOGGER,
            "runtime.apply_effects.complete",
            entity=context.source,
            outputs={"effect_count": 0, "effect_ids": []},
        )
        return

    effects_sorted = sorted(effects, key=lambda e: getattr(e, "priority", 0))

    log_trace(
        LOGGER,
        "runtime.apply_effects.start",
        entity=context.source,
        inputs={
            "context": context_snapshot(context),
            "effect_count": len(effects_sorted),
            "effect_ids": [entity_id(effect) for effect in effects_sorted],
        },
    )

    for effect in effects_sorted:
        emit_event("before_effect", context, effect=effect)

        try:
            effect.apply(context)
        except Exception as e:
            log_trace(
                LOGGER,
                "runtime.apply_effects.failed",
                entity=context.source,
                effect=effect,
                inputs={
                    "context": context_snapshot(context),
                    "effect_count": len(effects_sorted),
                },
                outputs={"effect_ids": [entity_id(item) for item in effects_sorted]},
                failure_state=describe_exception(e),
            )
            emit_event(
                "effect_failed",
                context,
                effect=effect,
                error=e,
            )
            raise

        emit_event("after_effect", context, effect=effect)

    emit_event("effects_applied", context)
    log_trace(
        LOGGER,
        "runtime.apply_effects.complete",
        entity=context.source,
        outputs={
            "effect_count": len(effects_sorted),
            "effect_ids": [entity_id(effect) for effect in effects_sorted],
        },
    )

def execute_ability(
    character,
    ability_name: str,
    explicit_targets=None,
    *,
    spent_amount: int | None = None,
    chosen_stat: str | None = None,
    metadata: dict | None = None,
    rebuild_after: bool = True,
):
    ability = None
    context = None
    targets = explicit_targets
    effects = []
    metadata = dict(metadata or {})

    log_trace(
        LOGGER,
        "runtime.execute_ability.start",
        entity=character,
        inputs={
            "ability_name": ability_name,
            "explicit_target_ids": [entity_id(target) for target in (explicit_targets or [])],
            "spent_amount": spent_amount,
            "chosen_stat": chosen_stat,
            "metadata": metadata,
            "rebuild_after": rebuild_after,
        },
    )

    try:
        ability = get_ability(ability_name)

        if getattr(ability, "is_passive", False):
            raise ValueError(f"'{ability.name}' is passive and cannot be activated")

        targets = explicit_targets or resolve_targets(character, ability)

        if chosen_stat is None and "chosen_stat" in metadata:
            chosen_stat = metadata["chosen_stat"]

        if getattr(ability, "cost", None) == "variable" and spent_amount is None:
            spent_amount = prompt_for_variable_cost(ability)

        prompted_metadata = prompt_for_context_options(ability)
        for key, value in prompted_metadata.items():
            metadata.setdefault(key, value)

        if chosen_stat is None and "chosen_stat" in metadata:
            chosen_stat = metadata["chosen_stat"]

        context = EffectContext(
            source=character,
            targets=targets,
            metadata=metadata,
            spent_amount=spent_amount or 0,
            chosen_stat=chosen_stat,
        )

        emit_event("ability_started", context, ability=ability)

        pool = getattr(ability, "cost_pool", None) or "fortune"
        cost = getattr(ability, "cost", 0)

        if cost == "variable":
            effects.append(SpendResource(pool, context.spent_amount))
        elif isinstance(cost, int) and cost > 0:
            effects.append(SpendResource(pool, cost))

        has_execute = getattr(ability, "execute", None) is not None
        has_effect_generator = getattr(ability, "effect_generator", None) is not None

        if has_execute and has_effect_generator:
            raise ValueError(
                f"Ability '{ability.name}' cannot define both execute and effect_generator"
            )

        if has_effect_generator:
            generated = ability.effect_generator(context)
            if generated:
                effects.extend(generated)

        elif has_execute:
            generated = ability.execute(character, targets)
            if generated:
                effects.extend(generated)

        else:
            static_effects = getattr(ability, "effects", None)
            if static_effects:
                effects.extend(static_effects)

        apply_effects(effects, context)

        emit_event("ability_resolved", context, ability=ability)

        if rebuild_after:
            recalculate(character)

        log_trace(
            LOGGER,
            "runtime.execute_ability.complete",
            entity=character,
            ability=ability,
            inputs={
                "context": context_snapshot(context),
                "rebuild_after": rebuild_after,
            },
            outputs={
                "target_ids": [entity_id(target) for target in targets],
                "effect_count": len(effects),
                "effect_ids": [entity_id(effect) for effect in effects],
            },
        )

        return {
            "ability": ability,
            "targets": targets,
            "context": context,
            "effects_applied": effects,
        }
    except Exception as error:
        log_trace(
            LOGGER,
            "runtime.execute_ability.failed",
            entity=character,
            ability=ability_name if ability is None else ability,
            inputs={
                "ability_name": ability_name,
                "target_ids": [entity_id(target) for target in (targets or [])],
                "context": context_snapshot(context),
                "metadata": metadata,
                "rebuild_after": rebuild_after,
            },
            outputs={
                "effect_count": len(effects),
                "effect_ids": [entity_id(effect) for effect in effects],
            },
            failure_state=describe_exception(error),
        )
        raise
