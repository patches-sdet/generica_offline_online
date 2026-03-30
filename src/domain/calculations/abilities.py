from domain.abilities import get_all_abilities

def collect_ability_effects(character):
    effects = []
    for ability in getattr(character, "abilities", []):
        if ability.is_unlocked(character):
            effects.extend(ability.effects)
    return effects

def rebuild_abilities(character, effects=None):
    character.abilities = [
        ability for ability in get_all_abilities()
        if ability.is_unlocked(character)
    ]
    print("ABILITIES:", len(get_all_abilities()))