def apply_effects(effects, character):
    for effect in effects:
        effect.apply(character)

def level_up(source, level_attr, character):
    # increment
    current_level = getattr(character, level_attr)
    setattr(character, level_attr, current_level + 1)

    # then apply the level up
    apply_effects(source.effects_per_level, character)

