from domain.attributes import Defenses, DEFENSE_KEYS
from .derived import get_derived_bonus, get_derived_override


def calculate_defenses(character):

    def resolve(stat: str):
        override = get_derived_override(character, stat)
        if override is not None:
            return override
        base = 0
        return base + get_derived_bonus(character, stat)

    values = {key: resolve(key) for key in DEFENSE_KEYS}

    character.defenses = Defenses(**values)
    return character.defenses
