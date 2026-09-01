def make_default_unlock(source_type: str, owner_name: str, required_level: int):
    def unlock(character):
        return character.get_progression_level(source_type, owner_name, 0) >= required_level

    return unlock
