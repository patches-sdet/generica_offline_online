def test_repeated_recalculation_no_drift():
    char = create_character("Test", "Human", "Archer", "Farmer")

    for _ in range(10):
        recalculate(char)

    baseline = create_character("Test", "Human", "Archer", "Farmer")

    assert char.attributes == baseline.attributes
