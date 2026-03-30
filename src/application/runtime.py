from domain.effects.base import EffectContext
from domain.effects import SpendResource
from domain.abilities.registry import get_ability
from application.targeting import resolve_targets
from application.events import emit_event

# Ability Execution

def execute_ability(character, ability_name: str, explicit_targets=None):
    ability = get_ability(ability_name)

    if not ability:
        raise ValueError(f"Ability '{ability_name}' not found")

    # TARGET RESOLUTION

    targets = explicit_targets or resolve_targets(character, ability)

    context = EffectContext(
        source=character,
        targets=targets,
    )

    # PRE-EXECUTION EVENT

    emit_event("ability_started", context, ability=ability)

    # BUILD EFFECT PIPELINE

    effects = []

    # COST → now an effect
    if ability.cost:
        pool = ability.cost_pool or "fortune"
        effects.append(SpendResource(pool, ability.cost))

    # ABILITY EFFECTS
    if ability.execute:
        ability_effects = ability.execute(character, targets) or []
        effects.extend(ability_effects)

    # APPLY EFFECTS

    apply_effects(effects, context)

    # POST-EXECUTION EVENT

    emit_event("ability_resolved", context, ability=ability)

# Effect Application Pipeline

def apply_effects(effects, context: EffectContext):
    if not effects:
        return

    # SORT BY PRIORITY

    effects_sorted = sorted(
        effects,
        key=lambda e: getattr(e, "priority", 0)
    )

    # APPLY EFFECTS

    for effect in effects_sorted:
        emit_event("before_effect", context, effect=effect)

        try:
            effect.apply(context)
        except Exception as e:
            emit_event(
                "effect_failed",
                context,
                effect=effect,
                error=e
            )
            raise

        emit_event("after_effect", context, effect=effect)

    # PIPELINE COMPLETE

    emit_event("effects_applied", context)
