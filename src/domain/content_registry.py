import importlib
import logging
import pkgutil
import sys

from domain.abilities.factory import Ability
from domain.advanced import ADVANCED_JOB_DEFINITIONS, AdvancedJob
from domain.adventure import ADVENTURE_JOB_DEFINITIONS, AdventureJob
from domain.profession import PROFESSION_JOB_DEFINITIONS, ProfessionJob
from domain.race import (
    BASE_RACE_DEFINITIONS,
    RACE_TEMPLATE_DEFINITIONS,
    BaseRace,
    RaceTemplate,
)
from observability import describe_exception, log_trace

# CANONICAL CONTENT REGISTRIES
AbilityGrant = tuple[str, int]
_BASE_RACE_REGISTRY: dict[str, BaseRace] = {}
_RACE_TEMPLATE_REGISTRY: dict[str, RaceTemplate] = {}
_ADVENTURE_JOB_REGISTRY: dict[str, AdventureJob] = {}
_PROFESSION_JOB_REGISTRY: dict[str, ProfessionJob] = {}
_ADVANCED_JOB_REGISTRY: dict[str, AdvancedJob] = {}
_ABILITY_REGISTRY: dict[str, Ability] = {}

# progression key: (ptype, progression_name)
_PROGRESSION_ABILITY_GRANTS: dict[tuple[str, str], list[AbilityGrant]] = {}

# guard to avoid repeated import-discovery work
_ABILITY_MODULES_INITIALIZED = False
LOGGER = logging.getLogger(__name__)

# RACE REGISTRATION / LOOKUP

def _get_from_registry(registry: dict, name: str, entity_type: str):
    """A generic registry lookup with consistent error handling."""
    try:
        return registry[name]
    except KeyError as exc:
        raise ValueError(f"{entity_type} '{name}' not registered") from exc

def _has_in_registry(registry: dict, name: str) -> bool:
    """A generic registry existence check."""
    return name in registry

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
    return _get_from_registry(_BASE_RACE_REGISTRY, name, "Base race")


def get_race_template(name: str) -> RaceTemplate:
    return _get_from_registry(_RACE_TEMPLATE_REGISTRY, name, "Race template")

def has_base_race(name: str) -> bool:
    return _has_in_registry(_BASE_RACE_REGISTRY, name)

def has_race_template(name: str) -> bool:
    return _has_in_registry(_RACE_TEMPLATE_REGISTRY, name)

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
    return _get_from_registry(_ADVENTURE_JOB_REGISTRY, name, "Adventure job")

def get_profession_job(name: str) -> ProfessionJob:
    return _get_from_registry(_PROFESSION_JOB_REGISTRY, name, "Profession job")

def get_advanced_job(name: str) -> AdvancedJob:
    return _get_from_registry(_ADVANCED_JOB_REGISTRY, name, "Advanced job")

def has_adventure_job(name: str) -> bool:
    return _has_in_registry(_ADVENTURE_JOB_REGISTRY, name)

def has_profession_job(name: str) -> bool:
    return _has_in_registry(_PROFESSION_JOB_REGISTRY, name)

def has_advanced_job(name: str) -> bool:
    return _has_in_registry(_ADVANCED_JOB_REGISTRY, name)

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
    return _get_from_registry(_ABILITY_REGISTRY, name, "Ability")

def has_ability(name: str) -> bool:
    return _has_in_registry(_ABILITY_REGISTRY, name)

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

def get_progression_ability_grants(ptype: str, progression_name: str,) -> tuple[AbilityGrant, ...]:
    return tuple(_PROGRESSION_ABILITY_GRANTS.get((ptype, progression_name), ()))

def get_progression_ability_names(ptype: str, progression_name: str) -> tuple[str, ...]:
    return tuple(
        ability_name
        for ability_name, _required_level in get_progression_ability_grants(ptype, progression_name)
    )

def get_unlocked_progression_ability_grants(
    ptype: str,
    progression_name: str,
    level: int,
) -> tuple[str, ...]:
    normalized_level = max(1, int(level))
    return tuple(
        ability_name
        for ability_name, required_level
        in get_progression_ability_grants(ptype, progression_name)
        if required_level <= normalized_level
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

    from domain.abilities import advanced as ability_advanced
    from domain.abilities import professions as ability_professions
    from domain.abilities import races as ability_races
    from domain.abilities.adventure import legacy_abilities as ability_definitions
    from domain.abilities.shared import combat as shared_combat
    from domain.abilities.shared import generic as shared_generic
    from domain.abilities.shared import stealth as shared_stealth
    from domain.abilities.shared import utility as shared_utility

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
    log_trace(
        LOGGER,
        "content.initialize.start",
        inputs={"force": force},
    )

    try:
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

        modules_loaded = initialize_ability_modules(force=force)

        log_trace(
            LOGGER,
            "content.initialize.complete",
            inputs={"force": force},
            outputs={
                "base_race_count": len(_BASE_RACE_REGISTRY),
                "race_template_count": len(_RACE_TEMPLATE_REGISTRY),
                "adventure_job_count": len(_ADVENTURE_JOB_REGISTRY),
                "profession_job_count": len(_PROFESSION_JOB_REGISTRY),
                "advanced_job_count": len(_ADVANCED_JOB_REGISTRY),
                "ability_count": len(_ABILITY_REGISTRY),
                "progression_grant_count": len(_PROGRESSION_ABILITY_GRANTS),
                "ability_modules_loaded": modules_loaded,
            },
        )
    except Exception as error:
        log_trace(
            LOGGER,
            "content.initialize.failed",
            inputs={"force": force},
            outputs={
                "base_race_count": len(_BASE_RACE_REGISTRY),
                "race_template_count": len(_RACE_TEMPLATE_REGISTRY),
                "adventure_job_count": len(_ADVENTURE_JOB_REGISTRY),
                "profession_job_count": len(_PROFESSION_JOB_REGISTRY),
                "advanced_job_count": len(_ADVANCED_JOB_REGISTRY),
                "ability_count": len(_ABILITY_REGISTRY),
                "progression_grant_count": len(_PROGRESSION_ABILITY_GRANTS),
            },
            failure_state=describe_exception(error),
        )
        raise

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
        "domain.abilities.adventure.",
        "domain.abilities.professions.",
        "domain.abilities.races.",
        "domain.abilities.advanced.",
    )

    for module_name in list(sys.modules):
        if module_name.startswith(reload_prefixes):
            del sys.modules[module_name]

    _ABILITY_MODULES_INITIALIZED = False
