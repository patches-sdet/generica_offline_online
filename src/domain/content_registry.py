import importlib, sys
import pkgutil
from domain.race import (
    BaseRace,
    RaceTemplate,
    BASE_RACE_DEFINITIONS,
    RACE_TEMPLATE_DEFINITIONS,
)
from domain.adventure import AdventureJob, ADVENTURE_JOB_DEFINITIONS
from domain.profession import ProfessionJob, PROFESSION_JOB_DEFINITIONS
from domain.advanced import AdvancedJob, ADVANCED_JOB_DEFINITIONS
from domain.abilities.factory import Ability

# CANONICAL CONTENT REGISTRIES

_BASE_RACE_REGISTRY: dict[str, BaseRace] = {}
_RACE_TEMPLATE_REGISTRY: dict[str, RaceTemplate] = {}
_ADVENTURE_JOB_REGISTRY: dict[str, AdventureJob] = {}
_PROFESSION_JOB_REGISTRY: dict[str, ProfessionJob] = {}
_ADVANCED_JOB_REGISTRY: dict[str, AdvancedJob] = {}
_ABILITY_REGISTRY: dict[str, Ability] = {}

# progression key: (ptype, progression_name)
_PROGRESSION_ABILITY_GRANTS: dict[tuple[str, str], list[tuple[str, int]]] = {}

# guard to avoid repeated import-discovery work
_ABILITY_MODULES_INITIALIZED = False

# RACE REGISTRATION / LOOKUP

def register_base_race(race: BaseRace) -> None:
    if race.name in _BASE_RACE_REGISTRY:
        raise ValueError(f"Base race already registered: {race.name}")
    _BASE_RACE_REGISTRY[race.name] = race


def register_race_template(template: RaceTemplate) -> None:
    if template.name in _RACE_TEMPLATE_REGISTRY:
        raise ValueError(f"Race template already registered: {template.name}")
    _RACE_TEMPLATE_REGISTRY[template.name] = template

def get_racial_progression_source(name: str):
    if has_base_race(name):
        return get_base_race(name)

    if has_race_template(name):
        return get_race_template(name)

    raise ValueError(f"Race progression '{name}' not registered")

def get_base_race(name: str) -> BaseRace:
    try:
        return _BASE_RACE_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Base race '{name}' not registered") from exc


def get_race_template(name: str) -> RaceTemplate:
    try:
        return _RACE_TEMPLATE_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Race template '{name}' not registered") from exc


def has_base_race(name: str) -> bool:
    return name in _BASE_RACE_REGISTRY


def has_race_template(name: str) -> bool:
    return name in _RACE_TEMPLATE_REGISTRY


def get_all_base_races() -> list[BaseRace]:
    return list(_BASE_RACE_REGISTRY.values())


def get_all_race_templates() -> list[RaceTemplate]:
    return list(_RACE_TEMPLATE_REGISTRY.values())

# JOB REGISTRATION / LOOKUP

def register_adventure_job(job: AdventureJob) -> None:
    if job.name in _ADVENTURE_JOB_REGISTRY:
        raise ValueError(f"Adventure job already registered: {job.name}")
    _ADVENTURE_JOB_REGISTRY[job.name] = job


def register_profession_job(job: ProfessionJob) -> None:
    if job.name in _PROFESSION_JOB_REGISTRY:
        raise ValueError(f"Profession job already registered: {job.name}")
    _PROFESSION_JOB_REGISTRY[job.name] = job


def register_advanced_job(job: AdvancedJob) -> None:
    if job.name in _ADVANCED_JOB_REGISTRY:
        raise ValueError(f"Advanced job already registered: {job.name}")
    _ADVANCED_JOB_REGISTRY[job.name] = job


def get_adventure_job(name: str) -> AdventureJob:
    try:
        return _ADVENTURE_JOB_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Adventure job '{name}' not registered") from exc


def get_profession_job(name: str) -> ProfessionJob:
    try:
        return _PROFESSION_JOB_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Profession job '{name}' not registered") from exc


def get_advanced_job(name: str) -> AdvancedJob:
    try:
        return _ADVANCED_JOB_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Advanced job '{name}' not registered") from exc


def has_adventure_job(name: str) -> bool:
    return name in _ADVENTURE_JOB_REGISTRY


def has_profession_job(name: str) -> bool:
    return name in _PROFESSION_JOB_REGISTRY


def has_advanced_job(name: str) -> bool:
    return name in _ADVANCED_JOB_REGISTRY


def get_all_adventure_jobs() -> list[AdventureJob]:
    return list(_ADVENTURE_JOB_REGISTRY.values())


def get_all_profession_jobs() -> list[ProfessionJob]:
    return list(_PROFESSION_JOB_REGISTRY.values())


def get_all_advanced_jobs() -> list[AdvancedJob]:
    return list(_ADVANCED_JOB_REGISTRY.values())

# ABILITY REGISTRATION / LOOKUP

def register_ability(ability: Ability) -> None:
    if ability.name in _ABILITY_REGISTRY:
        raise ValueError(f"Ability already registered: {ability.name}")
    _ABILITY_REGISTRY[ability.name] = ability


def get_ability(name: str) -> Ability:
    try:
        return _ABILITY_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Ability '{name}' not registered") from exc


def has_ability(name: str) -> bool:
    return name in _ABILITY_REGISTRY


def get_all_abilities() -> list[Ability]:
    return list(_ABILITY_REGISTRY.values())

# PROGRESSION -> ABILITY GRANTS

def register_progression_ability_grant(
    ptype: str,
    progression_name: str,
    ability_name: str,
    required_level: int = 1,
) -> None:
    if ability_name not in _ABILITY_REGISTRY:
        raise ValueError(
            f"Cannot grant unknown ability '{ability_name}' "
            f"to {ptype}:{progression_name}"
        )
    
    try:
        normalized_level = max(1, int(required_level))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid required level for: {ptype}:{progression_name} -> "
                            f"{ability_name}: {required_level!r}"
                            ) from exc

    key = (ptype, progression_name)
    _PROGRESSION_ABILITY_GRANTS.setdefault(key, [])

    grant = (ability_name, normalized_level)

    if grant not in _PROGRESSION_ABILITY_GRANTS[key]:
        _PROGRESSION_ABILITY_GRANTS[key].append(grant)

def get_progression_ability_grants(ptype: str, progression_name: str,) -> tuple[tuple[str, int], ...]:
    return tuple(_PROGRESSION_ABILITY_GRANTS.get((ptype, progression_name), ()))


def get_progression_ability_names(ptype: str, progression_name: str) -> tuple[str, ...]:
    return tuple(
        ability_name
        for ability_name, _required_level in get_progression_ability_grants(ptype, progression_name)
    )

# UNIFIED PROGRESSION SOURCE RESOLUTION

def get_progression_source(ptype: str, name: str):
    if ptype == "race":
        return get_racial_progression_source(name)

    if ptype == "adventure":
        return get_adventure_job(name)

    if ptype == "profession":
        return get_profession_job(name)

    if ptype == "advanced":
        return get_advanced_job(name)

    raise ValueError(f"Unknown progression type: {ptype}")

# BOOTSTRAP HELPERS

def _import_modules_from_package(package) -> int:
    loaded = 0

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name.startswith("_"):
            continue

        importlib.import_module(f"{package.__name__}.{module_name}")
        loaded += 1

    return loaded

def initialize_ability_modules(force: bool = False) -> int:
    global _ABILITY_MODULES_INITIALIZED

    if _ABILITY_MODULES_INITIALIZED and not force:
        return 0

    from domain.abilities.shared import combat as shared_combat
    from domain.abilities.shared import stealth as shared_stealth
    from domain.abilities.shared import utility as shared_utility
    from domain.abilities.shared import generic as shared_generic

    from domain.abilities import advanced as ability_advanced
    from domain.abilities import definitions as ability_definitions
    from domain.abilities import professions as ability_professions
    from domain.abilities import races as ability_races

    loaded = 0

    # shared first
    for group in (shared_combat, shared_stealth, shared_utility, shared_generic):
        loaded += _import_modules_from_package(group)

    # progression content second
    for group in (
        ability_definitions,
        ability_professions,
        ability_races,
        ability_advanced,
    ):
        loaded += _import_modules_from_package(group)

    _ABILITY_MODULES_INITIALIZED = True
    return loaded

def initialize_content_registries(force: bool = False) -> None:
    """
    Canonical startup hook for static content.

    Safe to call multiple times:
    - base content is only registered once
    - ability modules are only imported once unless forced
    """
    if force:
        clear_content_registries()

    for race in BASE_RACE_DEFINITIONS:
        if race.name not in _BASE_RACE_REGISTRY:
            register_base_race(race)

    for template in RACE_TEMPLATE_DEFINITIONS:
        if template.name not in _RACE_TEMPLATE_REGISTRY:
            register_race_template(template)

    for job in ADVENTURE_JOB_DEFINITIONS:
        if job.name not in _ADVENTURE_JOB_REGISTRY:
            register_adventure_job(job)

    for job in PROFESSION_JOB_DEFINITIONS:
        if job.name not in _PROFESSION_JOB_REGISTRY:
            register_profession_job(job)

    for job in ADVANCED_JOB_DEFINITIONS:
        if job.name not in _ADVANCED_JOB_REGISTRY:
            register_advanced_job(job)

    initialize_ability_modules(force=force)

def clear_content_registries() -> None:
    global _ABILITY_MODULES_INITIALIZED

    # Static content registries
    _BASE_RACE_REGISTRY.clear()
    _RACE_TEMPLATE_REGISTRY.clear()
    _ADVENTURE_JOB_REGISTRY.clear()
    _PROFESSION_JOB_REGISTRY.clear()
    _ADVANCED_JOB_REGISTRY.clear()

    # Ability / grant registries
    _ABILITY_REGISTRY.clear()
    _PROGRESSION_ABILITY_GRANTS.clear()

    # Remove imported content modules so top-level build_* calls execute again
    reload_prefixes = (
        "domain.abilities.shared.",
        "domain.abilities.definitions.",
        "domain.abilities.professions.",
        "domain.abilities.races.",
        "domain.abilities.advanced.",
    )

    for module_name in list(sys.modules):
        if module_name.startswith(reload_prefixes):
            del sys.modules[module_name]

    _ABILITY_MODULES_INITIALIZED = False