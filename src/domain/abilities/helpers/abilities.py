def ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name, 0)


def ctx_ability_level(ctx, ability_name: str) -> int:
    return ctx.source.get_ability_effective_level(ability_name, 0)


def progression_level(character, progression_type: str, progression_name: str) -> int:
    return character.get_progression_level(progression_type, progression_name, 0)


def ctx_progression_level(ctx, progression_type: str, progression_name: str) -> int:
    return ctx.source.get_progression_level(progression_type, progression_name, 0)