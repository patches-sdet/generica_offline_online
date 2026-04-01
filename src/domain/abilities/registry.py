from typing import Dict, List

from domain.race import Race
from domain.adventure import AdventureJob
from domain.profession import ProfessionJob
from domain.advanced import AdvancedJob
from .factory import Ability

_RACE_REGISTRY: Dict[str, Race] = {}
_ADVENTURE_JOB_REGISTRY: Dict[str, AdventureJob] = {}
_PROFESSION_JOB_REGISTRY: Dict[str, ProfessionJob] = {}
_ADVANCED_JOB_REGISTRY: Dict[str, AdvancedJob] = {}
_ABILITY_REGISTRY: Dict[str, Ability] = {}

def register_race(race: Race):
    if race.name in _RACE_REGISTRY:
        raise ValueError(f"Race already registered: {race.name}")
    _RACE_REGISTRY[race.name] = race

def register_adventure_job(job: AdventureJob):
    if job.name in _ADVENTURE_JOB_REGISTRY:
        raise ValueError(f"Adventure job already registered: {job.name}")
    _ADVENTURE_JOB_REGISTRY[job.name] = job

def register_profession_job(job: ProfessionJob):
    if job.name in _PROFESSION_JOB_REGISTRY:
        raise ValueError(f"Profession job already registered: {job.name}")
    _PROFESSION_JOB_REGISTRY[job.name] = job

def register_advanced_job(job):
    if job.name in _ADVANCED_JOB_REGISTRY:
        raise ValueError(f"Advanced job already registered: {job.name}")
    _ADVANCED_JOB_REGISTRY[job.name] = job

def register_ability(ability: Ability):
    if ability.name in _ABILITY_REGISTRY:
        raise ValueError(f"Ability already registered: {ability.name}") # this needs to check if the existing ability is a skill, and if so, 
                                                                        # increase the existing ability level by 5, or ignore it if it's passive 
                                                                        # or a non-skill active ability, and if the new ability is not a skill, 
                                                                        # then it should just ignore it
    _ABILITY_REGISTRY[ability.name] = ability

def get_ability(name: str) -> Ability:
    return _ABILITY_REGISTRY[name]


def get_all_abilities() -> List[Ability]:
    return list(_ABILITY_REGISTRY.values())