def test_spend_resource():
    char = create_character(...)

    initial = char.pools["fortune"][0]

    spend(char, "fortune", 5)

    assert char.pools["fortune"][0] == initial - 5
