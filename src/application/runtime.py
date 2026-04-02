from domain.effects.base import EffectContext
from domain.effects import SpendResource
from domain.calculations import recalculate
from domain.content_registry import get_ability

from application.targeting import resolve_targets
from application.events import emit_event


def prompt_for_variable_cost(ability) -> int:
    pool_name = ability.cost_pool or "fortune"

    while True:
        raw = input(f"Enter {pool_name} to spend for {ability.name}: ").strip()

        if not raw.isdigit():
            print("Please enter a non-negative whole number.")
            continue

        return int(raw)


def prompt_for_context_options(ability) -> dict:
    metadata = {}

    if getattr(ability, "requires_chosen_stat", False):
        metadata["chosen_stat"] = input("Choose a stat: ").strip().lower()

    return metadata


def apply_effects(effects, context: EffectContext):
    if not effects:
        return

    effects_sorted = sorted(effects, key=lambda e: getattr(e, "priority", 0))

    for effect in effects_sorted:
        emit_event("before_effect", context, effect=effect)

        try:
            effect.apply(context)
        except Exception as e:
            emit_event(
                "effect_failed",
                context,
                effect=effect,
                error=e,
            )
            raise

        emit_event("after_effect", context, effect=effect)

    emit_event("effects_applied", context)


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
    ability = get_ability(ability_name)

    if getattr(ability, "is_passive", False):
        raise ValueError(f"'{ability.name}' is passive and cannot be activated")

    targets = explicit_targets or resolve_targets(character, ability)

    metadata = dict(metadata or {})

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

    effects = []

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

    return {
        "ability": ability,
        "targets": targets,
        "context": context,
        "effects_applied": effects,
    }