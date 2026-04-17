import pytest
from domain.character import Character
from domain.progression import Progression
from application.skill_validation import (
    validate_generic_skill_cap,
    validate_job_skill_cap,
)


def test_job_skill_cap_respects_five_times_job_level():
    c = Character(name="Test")
    c.progressions[("adventure", "Berserker")] = Progression(
        type="adventure",
        name="Berserker",
        level=2,
    )

    validate_job_skill_cap(c, "Berserker", "Growl", 10)

    with pytest.raises(ValueError):
        validate_job_skill_cap(c, "Berserker", "Growl", 11)


def test_generic_skill_cap_respects_five_times_race_level():
    c = Character(name="Test")
    c.progressions[("race", "Bear")] = Progression(
        type="race",
        name="Bear",
        level=3,
    )

    validate_generic_skill_cap(c, "Riding", 15)

    with pytest.raises(ValueError):
        validate_generic_skill_cap(c, "Riding", 16)