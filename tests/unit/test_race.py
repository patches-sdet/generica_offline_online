from domain.race import BASE_RACE_DEFINITIONS


def test_orc_level_effects_repeat_correctly():
    orc = next(r for r in BASE_RACE_DEFINITIONS if r.name == "Orc")

    effects = orc.get_effects(3)

    assert len(effects) == 4