from domain.race_resolution import get_race_tags
from domain.content_registry import get_progression_source
from domain.effects.special.tag import ApplyTagEffect


def rebuild_tags(character, effects):
    tags = set()

    # Race/base/template tags
    tags.update(get_race_tags(character))

    # Progression-source tags
    for progression in character.progressions.values():
        source = get_progression_source(progression.type, progression.name)
        if source and hasattr(source, "tags"):
            tags.update(source.tags)

    # Effect-applied tags
    for effect in effects:
        if isinstance(effect, ApplyTagEffect):
            tags.add(effect.tag)

    character.tags = tags