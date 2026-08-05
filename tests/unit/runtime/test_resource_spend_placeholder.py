from application.runtime import execute_ability
from domain.abilities.factory import make_ability
from domain.character import Character
from domain.content_registry import initialize_content_registries, register_ability


def test_execute_ability_spends_sanity_from_registered_runtime_skill(clean_registries):
    initialize_content_registries(force=True)

    character = Character(name="Resource Spend Test")
    character.current_sanity = 50
    character.max_sanity = 50

    ability = make_ability(
        name="Runtime Spend Test Ability",
        unlock_condition=lambda _: True,
        execute=lambda caster, targets: [],
        cost=5,
        cost_pool="sanity",
        is_skill=True,
        auto_register=False,
    )
    register_ability(ability)

    before_sanity = character.current_sanity

    result = execute_ability(character, "Runtime Spend Test Ability", explicit_targets=[character])

    assert result["ability"].name == "Runtime Spend Test Ability"
    assert character.current_sanity == before_sanity - 5
