from application.runtime import apply_damage
from domain.calculations import recalculate
from domain.character import Character
from domain.skill_ownership import add_skill_levels


def test_hp_damage_above_toughness_threshold_ranks_up_toughness_and_increases_max_hp(
    clean_registries,
):
    from domain.content_registry import initialize_content_registries

    initialize_content_registries(force=True)

    character = Character(name="Toughness Runtime Test")
    add_skill_levels(character, "Toughness", source="job_points:Berserker", levels=5)
    recalculate(character)
    character.current_hp = character.max_hp

    before_rank = character.get_skill_level("Toughness", 0)
    before_max_hp = character.max_hp
    constitution = character.get_stat("constitution")

    result = apply_damage(character, pool="hp", amount=constitution + before_rank + 1)

    assert result["toughness_rank_up"] == 1
    assert character.get_skill_level("Toughness", 0) == before_rank + 1
    assert character.max_hp == before_max_hp + 2
