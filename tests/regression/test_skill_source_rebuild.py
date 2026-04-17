from domain.content_registry import initialize_content_registries
from domain.character import Character
from domain.skill_ownership import set_skill_levels
from domain.calculations import recalculate


def test_recalculate_consumes_and_preserves_skill_sources():
    initialize_content_registries(force=True)

    c = Character(name="Test")
    set_skill_levels(c, "Dodge", source="generic_points", levels=5)

    recalculate(c)

    assert c.skill_sources["Dodge"]["generic_points"] == 5
    assert c.get_ability_effective_level("Dodge") == 5