from domain.content_registry import initialize_content_registries
from domain.character import Character
from application.runtime import award_generic_skill


def test_award_generic_skill_only_awards_once():
    initialize_content_registries(force=True)

    c = Character(name="Test")

    first = award_generic_skill(c, "Riding")
    second = award_generic_skill(c, "Riding")

    assert first is True
    assert second is False