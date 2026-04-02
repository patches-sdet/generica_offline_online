from typing import Optional

from domain.effects import DerivedStatOverride
from domain.effects.base import Effect
from domain.content_registry import get_base_race, get_race_template
from domain.race import build_crossbreed_race


MATERIAL_EFFECTS: dict[str, list[Effect]] = {
    "cloth": [
        DerivedStatOverride("armor", 10),
        DerivedStatOverride("endurance", 20),
    ],
    "leather": [
        DerivedStatOverride("armor", 15),
        DerivedStatOverride("endurance", 15),
    ],
    "metal": [
        DerivedStatOverride("armor", 20),
        DerivedStatOverride("endurance", 10),
    ],
}


def _merge_tags(*tag_groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []

    for group in tag_groups:
        for tag in group:
            if tag not in ordered:
                ordered.append(tag)

    return tuple(ordered)


def _get_race_bases(character) -> list[str]:
    race_bases = list(getattr(character, "race_bases", []) or [])

    if race_bases:
        return race_bases

    # Compatibility fallback for older character objects
    progressions = getattr(character, "progressions", {}) or {}
    return [
        name
        for (ptype, name), progression in progressions.items()
        if ptype == "race" and getattr(progression, "level", 0) > 0
    ]


def _get_template_name(character) -> Optional[str]:
    # Prefer explicit field, then states fallback
    template_name = getattr(character, "race_template", None)
    if template_name:
        return template_name

    states = getattr(character, "states", {}) or {}
    return states.get("race_template")


def _get_material_name(character) -> Optional[str]:
    material = getattr(character, "race_material", None)
    if material:
        return material

    states = getattr(character, "states", {}) or {}
    return states.get("race_material")


def get_race_effects(character) -> list[Effect]:
    effects: list[Effect] = []

    base_names = _get_race_bases(character)
    template_name = _get_template_name(character)
    material = _get_material_name(character)

    template = get_race_template(template_name) if template_name else None

    if not base_names:
        return effects

    # Composition template: Crossbreed
    if template and template.kind == "composition":
        if template.name != "Crossbreed":
            raise ValueError(f"Unsupported composition template: {template.name}")

        if len(base_names) != 2:
            raise ValueError("Crossbreed requires exactly two parent races")

        parent_a = get_base_race(base_names[0])
        parent_b = get_base_race(base_names[1])
        composite = build_crossbreed_race(parent_a, parent_b)

        level_a = character.get_progression_level("race", base_names[0], 0)
        level_b = character.get_progression_level("race", base_names[1], 0)
        level = max(1, min(level_a, level_b))

        effects.extend(composite.effects_on_acquire())
        effects.extend(composite.get_effects(level))
        return effects

    # Normal base race handling
    highest_base_level = 1

    for base_name in base_names:
        base = get_base_race(base_name)
        level = max(1, character.get_progression_level("race", base_name, 0))
        highest_base_level = max(highest_base_level, level)

        effects.extend(base.effects_on_acquire())
        effects.extend(base.get_effects(level))

    # Overlay template handling
    if template and template.kind == "overlay":
        effects.extend(template.effects_on_acquire())
        effects.extend(template.get_effects(highest_base_level))

        if template.requires_material:
            if material is None:
                raise ValueError(f"{template.name} requires a material")
            try:
                effects.extend(MATERIAL_EFFECTS[material])
            except KeyError as exc:
                raise ValueError(f"Unknown material: {material}") from exc

    return effects


def get_race_tags(character) -> tuple[str, ...]:
    base_names = _get_race_bases(character)
    template_name = _get_template_name(character)

    template = get_race_template(template_name) if template_name else None

    if template and template.kind == "composition":
        if template.name != "Crossbreed":
            raise ValueError(f"Unsupported composition template: {template.name}")

        if len(base_names) != 2:
            raise ValueError("Crossbreed requires exactly two parent races")

        parent_a = get_base_race(base_names[0])
        parent_b = get_base_race(base_names[1])
        composite = build_crossbreed_race(parent_a, parent_b)
        return composite.tags

    tags: tuple[str, ...] = tuple()

    for base_name in base_names:
        tags = _merge_tags(tags, get_base_race(base_name).tags)

    if template:
        tags = _merge_tags(tags, template.tags)

    return tags


def get_race_display_name(character) -> str:
    base_names = _get_race_bases(character)
    template_name = _get_template_name(character)
    material = _get_material_name(character)

    if not base_names:
        return "Unknown"

    if template_name == "Crossbreed" and len(base_names) == 2:
        return f"Crossbreed ({base_names[0]}/{base_names[1]})"

    if template_name:
        if material:
            if len(base_names) == 1:
                return f"{material.title()} {template_name} ({base_names[0]})"
            return f"{material.title()} {template_name}"
        if len(base_names) == 1:
            return f"{template_name} ({base_names[0]})"
        return template_name

    if len(base_names) == 1:
        return base_names[0]

    return ", ".join(base_names)