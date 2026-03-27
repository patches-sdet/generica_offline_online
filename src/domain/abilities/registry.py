from typing import Dict, List

from .factory import Ability

_ABILITY_REGISTRY: Dict[str, Ability] = {}


def register_ability(ability: Ability):
    if ability.name in _ABILITY_REGISTRY:
        raise ValueError(f"Ability already registered: {ability.name}")

    _ABILITY_REGISTRY[ability.name] = ability


def get_ability(name: str) -> Ability:
    return _ABILITY_REGISTRY[name]


def get_all_abilities() -> List[Ability]:
    return list(_ABILITY_REGISTRY.values())
