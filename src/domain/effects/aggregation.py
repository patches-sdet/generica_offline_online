import logging
from typing import TYPE_CHECKING

from domain.content_registry import get_progression_source
from domain.effects.base import Effect
from domain.race_resolution import get_race_effects
from observability import describe_exception, entity_id, log_trace

if TYPE_CHECKING:
    from domain.character import Character


LOGGER = logging.getLogger(__name__)

# This maintains that everything is a flattened effect and not full of nested lists
def _extend_flat_effects(effects: list[Effect], result, source_name: str) -> None:
    if result is None:
        return

    if not isinstance(result, list):
        raise TypeError(
            f"{source_name} returned {type(result).__name__}, expected list[Effect]"
        )

    for item in result:
        if isinstance(item, list):
            raise TypeError(f"{source_name} returned nested list of effects")
        if not isinstance(item, Effect):
            raise TypeError(
                f"{source_name} returned {type(item).__name__}, expected Effect"
            )
        effects.append(item)


def collect_effects(character: "Character") -> list[Effect]:
    effects: list[Effect] = []
    current_source = None

    log_trace(
        LOGGER,
        "effects.collect.start",
        entity=character,
        inputs={
            "progression_count": len(getattr(character, "progressions", {})),
            "ability_count": len(getattr(character, "abilities", [])),
            "equipment_count": len(getattr(character, "equipment", [])),
            "inventory_count": len(getattr(character, "inventory", [])),
            "active_effect_count": len(getattr(character, "active_effects", [])),
        },
    )

    try:
        # Racial effects separated due to complexity

        for (ptype, name), progression in character.progressions.items():
            if ptype != "race":
                continue

            level = progression.level
            if level <= 1:
                continue

            source = get_progression_source(ptype, name)

            if hasattr(source, "effects_per_level"):
                current_source = f"{ptype}:{name}.effects_per_level"
                per_level = list(source.effects_per_level) * (level - 1)
                _extend_flat_effects(effects, per_level, current_source)

        # Progression effects

        for (ptype, name), progression in character.progressions.items():
            if ptype == "race":
                continue
            level = progression.level
            if level <= 0:
                continue

            source = get_progression_source(ptype, name)

            if hasattr(source, "get_effects"):
                current_source = f"{ptype}:{name}.get_effects"
                generated = source.get_effects(level)
                _extend_flat_effects(effects, generated, current_source)

        # Passive ability handling

        for ability in getattr(character, "abilities", []):
            if not getattr(ability, "is_passive", False):
                continue

            effect_generator = getattr(ability, "effect_generator", None)
            if not effect_generator:
                continue

            current_source = f"passive ability {ability.name}"
            generated = effect_generator(character)
            _extend_flat_effects(effects, generated, current_source)

        # Equipment (Not yet implemented)

        for item in getattr(character, "equipment", []):
            if not hasattr(item, "get_effects"):
                continue

            current_source = f"equipment {getattr(item, 'name', item.__class__.__name__)}"
            generated = item.get_effects()
            _extend_flat_effects(effects, generated, current_source)

        # Maybe use this for inventory stuff?

        for item in getattr(character, "inventory", []):
            if not getattr(item, "equipped", False):
                continue
            if not hasattr(item, "get_effects"):
                continue

            current_source = f"inventory item {getattr(item, 'name', item.__class__.__name__)}"
            generated = item.get_effects()
            _extend_flat_effects(effects, generated, current_source)

        # Active Skills/Effects

        for effect in getattr(character, "active_effects", []):
            effects.append(effect)

        log_trace(
            LOGGER,
            "effects.collect.complete",
            entity=character,
            outputs={
                "effect_count": len(effects),
                "effect_ids": [entity_id(effect) for effect in effects],
            },
        )
        return effects
    except Exception as error:
        log_trace(
            LOGGER,
            "effects.collect.failed",
            entity=character,
            inputs={"current_source": current_source},
            outputs={"effect_count": len(effects)},
            failure_state=describe_exception(error),
        )
        raise
