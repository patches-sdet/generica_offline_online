from presentation.character_sheet import ATTRIBUTE_NAMES


def format_effects(effects):
    parts = []

    for effect in effects:
        if hasattr(effect, "stats"):
            for stat, value in effect.stats.items():
                name = ATTRIBUTE_NAMES.get(stat, stat.title())
                parts.append(f"{value:+d} {name}")

        elif hasattr(effect, "stat") and hasattr(effect, "amount"):
            name = ATTRIBUTE_NAMES.get(effect.stat, effect.stat.title())
            parts.append(f"{effect.amount:+d} {name}")

    return ", ".join(parts)


def print_named_options(title: str, names: list[str]) -> None:
    print(title)
    for name in names:
        print(f"- {name}")


def print_job_options(title: str, jobs, *, include_effects: bool = True) -> None:
    print(title)
    for job in jobs:
        suffix = ""
        if include_effects:
            bonuses = format_effects(getattr(job, "effects_on_acquire", []))
            suffix = f" ({bonuses})" if bonuses else ""
        print(f"- {job.name}{suffix}")


def print_active_abilities(active_abilities) -> None:
    print("Available Active Abilities:")
    for index, ability in enumerate(active_abilities, 1):
        details = []

        if getattr(ability, "is_skill", False):
            details.append("Skill")

        if getattr(ability, "cost", 0):
            pool = getattr(ability, "cost_pool", None) or "resource"
            details.append(f"Cost: {ability.cost} {pool.capitalize()}")

        if getattr(ability, "duration", None):
            details.append(f"Duration: {ability.duration}")

        suffix = f" [{' | '.join(details)}]" if details else ""
        print(f"{index}. {ability.name}{suffix}")


def print_progressions(title: str, progressions) -> None:
    print(title)
    for index, progression in enumerate(progressions, 1):
        print(f"{index}. {progression.name} Lv. {progression.level}")


def print_attribute_values(character) -> list[str]:
    stats = list(ATTRIBUTE_NAMES.keys())
    print("Available attributes:")

    for index, stat in enumerate(stats, 1):
        display = ATTRIBUTE_NAMES.get(stat, stat.title())
        print(f"{index}. {display}: {character.get_stat(stat)}")

    return stats
