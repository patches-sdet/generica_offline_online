from domain.character import Character
from domain.effects import EffectContext, Effect


def rebuild_attributes(character: Character, effects: list):
    """
    Fully rebuild base + additive attributes ONLY.
    No derived stats here.
    """

    race_level = character.get_race_levels()

#    character.attributes = character.race.get_base_attributes(race_level)

    # Reset tracking
    character._attribute_sources.clear()

    # ROLL EFFECTS (STATIC)

    context = EffectContext(source="roll", targets=[character])

    for effect in character.attribute_effects:
        effect.apply(context)

    # RACE EFFECTS

    race_level = character.get_race_levels()
    
    context = EffectContext(
            source="race", 
            targets=[character]
        )

    for effect in character.race.get_effects(race_level):
        effect.apply(context)

    # Snapshot base AFTER race
    character._base_attributes = dict(vars(character.attributes))

    # ADVENTURE JOBS

    for job in character.adventure_jobs:
        level = character.adventure_levels.get(job.name, 1)

        context = EffectContext(
            source=f"job:{job.name}",
            targets=[character],
        )

        for effect in job.get_effects(level):
            effect.apply(context)

    # PROFESSIONS

    for job in character.profession_jobs:
        level = character.profession_levels.get(job.name, 1)

        context = EffectContext(
            source=f"profession:{job.name}",
            targets=[character],
        )

        for effect in job.get_effects(level):
            effect.apply(context)
