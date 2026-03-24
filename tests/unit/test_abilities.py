def test_ability_unlock_condition():
    char = make_character_with_job("Animator")

    abilities = get_available_abilities(char)

    assert any(a.name == "Eye for Detail" for a in abilities)
