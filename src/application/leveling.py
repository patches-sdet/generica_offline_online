from __future__ import annotations
from domain.calculations import recalculate
from domain.skill_ownership import add_skill_levels
from domain.attributes import ATTRIBUTE_NAMES

def can_spend_level_points(character, amount: int) -> bool:
    if amount < 0:
        raise ValueError(f"Level point amount cannot be negative: {amount}")
    return character.level_points >= amount

def award_level_points(character, amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"Awarded level points must be positive: {amount}")
    character.level_points += amount

def spend_level_points(character, amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"Spent level points must be positive: {amount}")
    if not can_spend_level_points(character, amount):
        raise ValueError(f"Not enough level points: need {amount}, have {character.level_points}")
    character.level_points -= amount

def can_spend_grind_points(character, amount: int) -> bool:
    if amount < 0:
        raise ValueError(f"Grind point amount cannot be negative: {amount}")
    return character.grind_points >= amount

def award_grind_points(character, amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"Awarded grind points must be positive: {amount}")
    character.grind_points += amount

def spend_grind_points(character, amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"Spent grind points must be positive: {amount}")
    if not can_spend_grind_points(character, amount):
        raise ValueError(
            f"Not enough grind points: need {amount}, have {character.grind_points}"
        )
    character.grind_points -= amount

def increase_skill_from_runtime_use(
    character,
    skill_name: str,
    source: str = "runtime:rank_up",
    ranks: int = 1,
) -> None:
    if ranks <= 0:
        raise ValueError(f"Runtime skill ranks must be positive: {skill_name} -> {ranks}")

    add_skill_levels(character, skill_name, source=source, levels=ranks)
    recalculate(character)

    new_level = character.get_skill_level(skill_name, 0)
    print(f"Your {skill_name} skill is now level {new_level}!")

def level_up_progression(
    character,
    *,
    ptype: str,
    name: str,
    amount: int = 1,
    refill_pools: bool = True,
) -> int:
    """
    Low-level progression increment helper.

    Returns the new progression level.
    """
    missing_hp = max(0, character.max_hp - character.current_hp)

    character.increment_progression(ptype, name, amount=amount)
    recalculate(character)

    if refill_pools:
        character.current_hp = max(0, character.max_hp - missing_hp)
        character.current_sanity = character.max_sanity
        character.current_stamina = character.max_stamina
        character.current_moxie = character.max_moxie
        character.current_fortune = character.max_fortune

    return character.get_progression_level(ptype, name)

def acquire_new_progression(
    character,
    *,
    ptype: str,
    name: str,
    starting_level: int = 1,
    refill_pools: bool = True,
) -> int:
    """
    Used for new jobs / multiclass acquisition.
    """
    if character.has_progression(ptype, name):
        raise ValueError(f"Character already has progression {(ptype, name)}")

    character.add_progression(ptype, name, starting_level)
    recalculate(character)

    if refill_pools:
        character.current_sanity = character.max_sanity
        character.current_stamina = character.max_stamina
        character.current_moxie = character.max_moxie
        character.current_fortune = character.max_fortune

    return character.get_progression_level(ptype, name)

# SHARED JOB-LIKE HELPERS (ADVENTURE + ADVANCED)

def _get_plus_one_job_level_up_cost(character, *, ptype: str, job_name: str) -> int:
    current = character.get_progression_level(ptype, job_name, 0)
    if current <= 0:
        raise ValueError(f"Character does not have {ptype} job {job_name!r}")
    return current + 1


def _can_level_plus_one_job(character, *, ptype: str, job_name: str) -> bool:
    if not character.has_progression(ptype, job_name):
        return False

    cost = _get_plus_one_job_level_up_cost(character, ptype=ptype, job_name=job_name)
    return can_spend_level_points(character, cost)


def _level_plus_one_job(character, *, ptype: str, job_name: str, label: str) -> int:
    if not character.has_progression(ptype, job_name):
        raise ValueError(f"Character does not have {ptype} job {job_name!r}")

    cost = _get_plus_one_job_level_up_cost(character, ptype=ptype, job_name=job_name)
    spend_level_points(character, cost)

    new_level = level_up_progression(
        character,
        ptype=ptype,
        name=job_name,
        amount=1,
        refill_pools=True,
    )

    print(f"You are now a level {new_level} {job_name}!")
    return new_level


def _can_learn_new_plus_one_job(character, *, ptype: str, job_name: str) -> bool:
    if character.has_progression(ptype, job_name):
        return False
    return can_spend_level_points(character, 1)


def _learn_new_plus_one_job(character, *, ptype: str, job_name: str, label: str) -> int:
    if character.has_progression(ptype, job_name):
        raise ValueError(f"Character already has {ptype} job {job_name!r}")

    spend_level_points(character, 1)

    new_level = acquire_new_progression(
        character,
        ptype=ptype,
        name=job_name,
        starting_level=1,
        refill_pools=True,
    )

    print(f"You have unlocked the {job_name} job!")
    print(f"You are now a level {new_level} {job_name}!")

    return new_level

# ADVENTURE JOBS

def get_adventure_level_up_cost(character, job_name: str) -> int:
    return _get_plus_one_job_level_up_cost(
        character,
        ptype="adventure",
        job_name=job_name,
    )

def can_level_adventure_job(character, job_name: str) -> bool:
    return _can_level_plus_one_job(
        character,
        ptype="adventure",
        job_name=job_name,
    )

def level_adventure_job(character, job_name: str) -> int:
    return _level_plus_one_job(
        character,
        ptype="adventure",
        job_name=job_name,
        label="job",
    )

def can_learn_new_adventure_job(character, job_name: str) -> bool:
    return _can_learn_new_plus_one_job(
        character,
        ptype="adventure",
        job_name=job_name,
    )

def learn_new_adventure_job(character, job_name: str) -> int:
    return _learn_new_plus_one_job(
        character,
        ptype="adventure",
        job_name=job_name,
        label="job",
    )

# ADVANCED JOBS

def get_advanced_level_up_cost(character, job_name: str) -> int:
    return _get_plus_one_job_level_up_cost(
        character,
        ptype="advanced",
        job_name=job_name,
    )

def can_level_advanced_job(character, job_name: str) -> bool:
    return _can_level_plus_one_job(
        character,
        ptype="advanced",
        job_name=job_name,
    )

def level_advanced_job(character, job_name: str) -> int:
    return _level_plus_one_job(
        character,
        ptype="advanced",
        job_name=job_name,
        label="advanced job",
    )

def can_learn_new_advanced_job(character, job_name: str) -> bool:
    return _can_learn_new_plus_one_job(
        character,
        ptype="advanced",
        job_name=job_name,
    )

def learn_new_advanced_job(character, job_name: str) -> int:
    return _learn_new_plus_one_job(
        character,
        ptype="advanced",
        job_name=job_name,
        label="advanced job",
    )

# RACE PROGRESSION

def get_race_level_up_cost(character, race_name: str) -> int:
    current = character.get_race_level(race_name, 0)
    if current <= 0:
        raise ValueError(f"Character does not have race progression {race_name!r}")
    return current


def can_level_race_progression(character, race_name: str) -> bool:
    if not character.has_progression("race", race_name):
        return False

    cost = get_race_level_up_cost(character, race_name)
    return can_spend_level_points(character, cost)


def level_race_progression(character, race_name: str) -> int:
    """
    Rules-aware race progression level up.

    Current implementation:
    - costs current race level in level points
    - refills non-HP pools after rebuild
    - does not yet enforce the once-per-session rule

    TODO:
    - add session-state gating when that system exists
    """
    if not character.has_progression("race", race_name):
        raise ValueError(f"Character does not have race progression {race_name!r}")

    cost = get_race_level_up_cost(character, race_name)
    spend_level_points(character, cost)

    new_level = level_up_progression(
        character,
        ptype="race",
        name=race_name,
        amount=1,
        refill_pools=True,
    )

    print(f"You are now a level {new_level} {race_name}!")
    return new_level

# CRAFTING JOBS

def get_profession_level_up_cost(character, job_name: str) -> int:
    current = character.get_profession_level(job_name, 0)
    if current <= 0:
        raise ValueError(f"Character does not have profession job {job_name!r}")
    return 1


def can_level_profession_job(character, job_name: str) -> bool:
    if not character.has_progression("profession", job_name):
        return False

    cost = get_profession_level_up_cost(character, job_name)
    return can_spend_level_points(character, cost)


def level_profession_job(character, job_name: str) -> int:
    """
    Rules-aware profession/crafting job level up.

    Current implementation:
    - costs 1 level point per level gained
    - refills non-HP pools after rebuild
    - does not yet enforce:
        * recent crafting/use requirement
        * max two profession levels per session

    TODO:
    - add session-state / usage gating when that system exists
    """
    if not character.has_progression("profession", job_name):
        raise ValueError(f"Character does not have profession job {job_name!r}")

    cost = get_profession_level_up_cost(character, job_name)
    spend_level_points(character, cost)

    new_level = level_up_progression(
        character,
        ptype="profession",
        name=job_name,
        amount=1,
        refill_pools=True,
    )

    print(f"You are now a level {new_level} {job_name}!")
    return new_level

# ============================================================
# GRINDING
# ============================================================

def _ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def get_highest_job_level(character) -> int:
    highest = 0

    for ptype in ("adventure", "profession", "advanced"):
        for progression in character.get_progressions_by_type(ptype):
            highest = max(highest, progression.level)

    return highest


def get_related_skill_cap(character, skill_name: str) -> int:
    """
    Job skill cap: related job level * 5
    Generic skill cap: highest job level * 10

    Current heuristic:
    - if the skill is granted by any progression in race/adventure/profession/advanced,
      treat it as a job-like skill and use the highest related progression level * 5
    - otherwise treat it as a generic skill and use highest job level * 10
    """
    related_levels = []

    for ptype in ("race", "adventure", "profession", "advanced"):
        related_level = character.get_progression_level_for_ability(ptype, skill_name, 0)
        if related_level > 0:
            related_levels.append(related_level)

    if related_levels:
        return max(related_levels) * 5

    return get_highest_job_level(character) * 10


def get_skill_grind_cost(character, skill_name: str) -> int:
    current = character.get_skill_level(skill_name, 0)
    if current <= 0:
        raise ValueError(f"Character does not have skill {skill_name!r}")
    return _ceil_div(current, 10)


def can_grind_skill(character, skill_name: str) -> bool:
    current = character.get_skill_level(skill_name, 0)
    if current <= 0:
        return False

    cap = get_related_skill_cap(character, skill_name)
    if current >= cap:
        return False

    cost = get_skill_grind_cost(character, skill_name)
    return can_spend_grind_points(character, cost)


def grind_skill(
    character,
    skill_name: str,
    *,
    source: str = "grind",
    levels: int = 1,
) -> int:
    if levels != 1:
        raise ValueError("Current grind_skill implementation only supports levels=1")

    current = character.get_skill_level(skill_name, 0)
    if current <= 0:
        raise ValueError(f"Character does not have skill {skill_name!r}")

    cap = get_related_skill_cap(character, skill_name)
    if current >= cap:
        raise ValueError(
            f"Skill {skill_name!r} is already at or above its current cap ({cap})"
        )

    cost = get_skill_grind_cost(character, skill_name)
    spend_grind_points(character, cost)

    add_skill_levels(character, skill_name, source=source, levels=1)
    recalculate(character)

    new_level = character.get_skill_level(skill_name, 0)
    print(f"Your {skill_name} skill is now level {new_level}!")
    return new_level


def get_attribute_grind_cost(character, stat: str) -> int:
    if stat not in ATTRIBUTE_NAMES:
        raise ValueError(f"Unknown attribute for grinding: {stat!r}")

    current = character.get_stat(stat)
    if current <= 0:
        raise ValueError(f"Attribute {stat!r} is not grindable at value {current}")

    return _ceil_div(current, 5)


def can_grind_attribute(character, stat: str) -> bool:
    if stat not in ATTRIBUTE_NAMES:
        return False

    cost = get_attribute_grind_cost(character, stat)
    return can_spend_grind_points(character, cost)


def grind_attribute(
    character,
    stat: str,
    *,
    source: str = "grind",
    amount: int = 1,
) -> int:
    if stat not in ATTRIBUTE_NAMES:
        raise ValueError(f"Unknown attribute for grinding: {stat!r}")
    if amount != 1:
        raise ValueError("Current grind_attribute implementation only supports amount=1")

    cost = get_attribute_grind_cost(character, stat)
    spend_grind_points(character, cost)

    character.add_manual_attribute_increase(stat, amount, source)
    recalculate(character)

    new_value = character.get_stat(stat)
    print(f"Your {stat} attribute is now {new_value}!")
    return new_value