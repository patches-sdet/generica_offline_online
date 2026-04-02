from typing import TYPE_CHECKING
from domain.effects.base import Effect
from domain.content_registry import get_progression_source
from domain.race_resolution import get_race_effects

if TYPE_CHECKING:
    from domain.character import Character

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

    # Racial effects separated due to complexity

    _extend_flat_effects(effects, get_race_effects(character), "get_race_effects")

    # Progression effects

    for (ptype, name), progression in character.progressions.items():
        if ptype == "race":
            continue
        level = progression.level
        if level <= 0:
            continue

        source = get_progression_source(ptype, name)

        # Acquire effects are applied once at level 1
        acquire_effects = list(getattr(source, "effects_on_acquire", ()) or ())
        _extend_flat_effects(effects, acquire_effects, f"{ptype}:{name}.effects_on_acquire")

        # Level-up Effects
        if hasattr(source, "get_effects"):
            generated = source.get_effects(level)
            _extend_flat_effects(effects, generated, f"{ptype}:{name}.get_effects")

    # Passive ability handling

    for ability in getattr(character, "abilities", []):
        if not getattr(ability, "is_passive", False):
            continue

        effect_generator = getattr(ability, "effect_generator", None)
        if not effect_generator:
            continue

        generated = effect_generator(character)
        _extend_flat_effects(effects, generated, f"passive ability {ability.name}")

    # Equipment (Not yet implemented)

    for item in getattr(character, "equipment", []):
        if not hasattr(item, "get_effects"):
            continue

        generated = item.get_effects()
        _extend_flat_effects(
            effects,
            generated,
            f"equipment {getattr(item, 'name', item.__class__.__name__)}",
        )

    # Maybe use this for inventory stuff?

    for item in getattr(character, "inventory", []):
        if not getattr(item, "equipped", False):
            continue
        if not hasattr(item, "get_effects"):
            continue

        generated = item.get_effects()
        _extend_flat_effects(
            effects,
            generated,
            f"inventory item {getattr(item, 'name', item.__class__.__name__)}",
        )

    # Active Skills/Effects

    for effect in getattr(character, "active_effects", []):
        effects.append(effect)

    return effects