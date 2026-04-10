from domain.content_registry import clear_content_registries, initialize_content_registries
from application.character_creation import create_character


def test_lesser_healing_duplicate_stack():
    clear_content_registries()
    initialize_content_registries()

    character = create_character(
        name="Stack Test",
        base_race_names=["Human"],
        adventure_job_names=["Cleric", "Oracle"],
        profession_job_names=[],
    )

    lesser = [a for a in character.abilities if a.name == "Lesser Healing"]

    assert len(lesser) == 1
    assert character.ability_levels["Lesser Healing"] == 6