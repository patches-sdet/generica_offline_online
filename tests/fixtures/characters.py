def make_base_character():
    return create_character("Test", "Human", "Archer", "Farmer")


def make_golem_character():
    return create_character(
        "Test",
        "Golem",
        "Archer",
        "Farmer",
        base_race_name="Human",
        material="metal"
    )
