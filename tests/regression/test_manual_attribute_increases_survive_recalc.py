from application.character_creation import create_character, apply_manual_attribute_allocation
from domain.calculations import recalculate

def test_manual_attribute_allocation_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Manual Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before = c.get_stat("strength")

    apply_manual_attribute_allocation(c, {"strength": 5})

    after_allocation = c.get_stat("strength")
    assert after_allocation == before + 5

    recalculate(c)

    after_recalc = c.get_stat("strength")
    assert after_recalc == before + 5
    assert c.manual_attribute_increases["strength"]["creation:manual"] == 5