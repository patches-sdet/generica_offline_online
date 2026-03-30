from typing import Dict, List

from .factory import Ability

_ABILITY_REGISTRY: Dict[str, Ability] = {}


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
