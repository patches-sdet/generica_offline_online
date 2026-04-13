def validate_total_generic_points(allocations: dict[str, int], max_points: int = 50) -> None:
    total = sum(allocations.values())
    if total > max_points:
        raise ValueError(f"Generic skill allocation exceeds cap: {total} > {max_points}")


def validate_total_job_points(allocations: dict[str, dict[str, int]], max_points: int = 100) -> None:
    total = sum(
        levels
        for skill_map in allocations.values()
        for levels in skill_map.values()
    )
    if total > max_points:
        raise ValueError(f"Job skill allocation exceeds cap: {total} > {max_points}")


def validate_job_skill_cap(character, job_name: str, skill_name: str, levels: int) -> None:
    job_level = character.get_progression_level("adventure", job_name, 0)
    cap = job_level * 5
    if levels > cap:
        raise ValueError(
            f"{skill_name} exceeds cap for {job_name}: {levels} > {cap}"
        )


def validate_generic_skill_cap(character, skill_name: str, levels: int) -> None:
    """
    Generic skill cap is based on race job level.
    """
    race_job_level = 0

    if hasattr(character, "get_race_level"):
        # Replace with a more exact generic/racial skill accessor when implemented.
        # This is a placeholder for the next rules pass.
        race_job_level = max(
            (p.level for (ptype, _), p in character.progressions.items() if ptype == "race"),
            default=0,
        )

    cap = race_job_level * 5
    if levels > cap:
        raise ValueError(
            f"{skill_name} exceeds generic skill cap: {levels} > {cap}"
        )