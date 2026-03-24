def test_stat_increase_applies_correctly():
    char = make_base_character()
    effect = StatIncrease("strength", 5)

    effect.apply(char, source="test")

    assert char.attributes.strength == 30
