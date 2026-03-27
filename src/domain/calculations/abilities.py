# domain/calculations/abilities.py

from domain.abilities import get_all_abilities

def rebuild_abilities(character):
    character.abilities = [
        ability
        for ability in get_all_abilities()
        if ability.is_unlocked(character)
    ]
