from domain.calculations import recalculate


def level_up(character, level_attr: str):
    """
    Generic level up function.

    level_attr examples:
    - "race_level"
    - "adventure_level"
    - "profession_level"
    """

    # Increment level
    current_level = getattr(character, level_attr)
    setattr(character, level_attr, current_level + 1)

    # Rebuild all derived state
    recalculate(character)
