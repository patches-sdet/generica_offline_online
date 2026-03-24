def test_material_race_combination():
    golem = resolve_race("Golem")
    human = resolve_race("Human")

    new_race = apply_material_to_race(golem, human, "metal")

    assert new_race.material == "metal"
    assert new_race.base_race == "Human"
