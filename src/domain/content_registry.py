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
_PROGRESSION_ABILITY_GRANTS: dict[tuple[str, str], list[str]] = {}

# RACE REGISTRATION / LOOKUP

def register_base_race(race: BaseRace) -> None:
    if race.name in _BASE_RACE_REGISTRY:
        raise ValueError(f"Base race already registered: {race.name}")
    _BASE_RACE_REGISTRY[race.name] = race

def register_race_template(template: RaceTemplate) -> None:
    if template.name in _RACE_TEMPLATE_REGISTRY:
        raise ValueError(f"Race template already registered: {template.name}")
    _RACE_TEMPLATE_REGISTRY[template.name] = template

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
) -> None:
    
    # Record that a progression grants access to an ability definition.
    key = (ptype, progression_name)
    _PROGRESSION_ABILITY_GRANTS.setdefault(key, [])

    if ability_name not in _PROGRESSION_ABILITY_GRANTS[key]:
        _PROGRESSION_ABILITY_GRANTS[key].append(ability_name)

def get_progression_ability_names(ptype: str, progression_name: str) -> list[str]:
    return list(_PROGRESSION_ABILITY_GRANTS.get((ptype, progression_name), []))

# UNIFIED PROGRESSION SOURCE RESOLUTION

def get_progression_source(ptype: str, name: str):
    if ptype == "race":
        return get_base_race(name)

    if ptype == "adventure":
        return get_adventure_job(name)

    if ptype == "profession":
        return get_profession_job(name)

    if ptype == "advanced":
        return get_advanced_job(name)

    raise ValueError(f"Unknown progression type: {ptype}")

# BOOTSTRAP

def initialize_content_registries() -> None:

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

# TEST / DEV UTILITIES

def clear_content_registries() -> None:
    _BASE_RACE_REGISTRY.clear()
    _RACE_TEMPLATE_REGISTRY.clear()
    _ADVENTURE_JOB_REGISTRY.clear()
    _PROFESSION_JOB_REGISTRY.clear()
    _ADVANCED_JOB_REGISTRY.clear()
    _ABILITY_REGISTRY.clear()
    _PROGRESSION_ABILITY_GRANTS.clear()