from helpers.builders import make_character, add_progression
from domain.calculations import recalculate
from domain.calculations.pools import calculate_pools
from unit.calculations.test_pools import _CharacterStub


def snapshot(character):
    return {
        "attributes": dict(character.attributes.values),
        "defenses": {
            "armor": character.defenses.armor,
            "mental_fortitude": character.defenses.mental_fortitude,
            "endurance": character.defenses.endurance,
            "cool": character.defenses.cool,
            "fate": character.defenses.fate,
        },
        "pools": {
            "max_hp": character.max_hp,
            "max_sanity": character.max_sanity,
            "max_stamina": character.max_stamina,
            "max_moxie": character.max_moxie,
            "max_fortune": character.max_fortune,
        },
        "ability_levels": dict(character.ability_levels),
        "tags": sorted(character.tags),
    }

def test_calculate_pools_is_idempotent():
    character = _CharacterStub(toughness_rank=3)

    calculate_pools(character)
    first_hp = character.max_hp

    calculate_pools(character)
    second_hp = character.max_hp

    assert first_hp == second_hp
    
def test_recalculate_is_idempotent_for_same_inputs(initialized_content):
    character = make_character("Determinism Test")
    add_progression(character, "race", "Bear", 1)
    add_progression(character, "adventure", "Berserker", 1)

    recalculate(character)
    first = snapshot(character)

    recalculate(character)
    second = snapshot(character)

    assert first == second
