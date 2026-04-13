from domain.calculations import recalculate

def increase_skill_from_runtime_use(character, skill_name: str, source: str = "runtime:rank_up", ranks: int = 1) -> None:
    ...

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
