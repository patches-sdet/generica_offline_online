from domain.rolls import apply_success_experience
from domain.character import Character
from domain.calculations import recalculate


def make_character():
    c = Character(name="Test")
    recalculate(c)
    return c

def test_apply_success_experience_grants_on_success():
    c = make_character()

    result = apply_success_experience(
        c,
        success=True,
        attribute_name="strength",
        experience_die=9,
    )

    assert result.attribute_gained is True
    assert c.manual_attribute_increases["strength"]["experience"] >= 1


def test_apply_success_experience_does_not_grant_on_failure():
    c = make_character()
    before = c.manual_attribute_increases.get("strength", 0)

    result = apply_success_experience(
        c,
        success=False,
        attribute_name="strength",
        experience_die=9,
    )

    assert result.gained_anything is False
    assert c.manual_attribute_increases.get("strength", 0) == before