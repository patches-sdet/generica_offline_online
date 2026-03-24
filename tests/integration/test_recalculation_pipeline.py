def test_recalculate_applies_all_sources():
    char = create_character("Test", "Human", "Archer", "Farmer")

    original = char.attributes.strength

    recalculate(char)

    assert char.attributes.strength == original
