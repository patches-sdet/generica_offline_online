def test_same_input_same_output():
    c1 = create_character("Test", "Human", "Archer", "Farmer")
    c2 = create_character("Test", "Human", "Archer", "Farmer")

    assert c1.attributes == c2.attributes
