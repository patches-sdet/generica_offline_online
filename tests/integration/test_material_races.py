def test_golem_character_creation():
    char = create_character(
        "Test",
        "Golem",
        "Archer",
        "Farmer",
        base_race="Human",
        material="metal"
    )

    assert char.race.material == "metal"
    assert char.race.base_race == "Human"
