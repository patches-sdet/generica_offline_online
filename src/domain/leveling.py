


def apply_scaling(attributes, scaling):
    for stat, value in scaling.items():
        current = getattr(attributes, stat)
        setattr(attributes, stat, current + value)

def level_up(source, level_attr, character):
    setattr(character, level_attr, getattr(character, level_attr) + 1)
    apply_scaling(character.attributes, source.level_scaling)

level_up(character.race, "race_level", character)
level_up(character.adventure_job, "adventure_level", character)
