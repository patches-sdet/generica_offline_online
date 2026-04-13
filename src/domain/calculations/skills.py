from domain.skill_ownership import rebuild_skill_level_summary


def rebuild_skills(character) -> None:
    """
    Rebuild final character skill_levels from canonical skill_sources.
    """
    character.skill_levels.clear()
    character.skill_levels = rebuild_skill_level_summary(character)