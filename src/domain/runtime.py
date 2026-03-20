def _modify_current(character, pool_name: str, amount: int):
    current_attr = f"current_{pool_name}"

    current = getattr(character, current_attr)

    max_value = getattr(calculate_pools(character), pool_name)[1]

    new_value = max(0, min(max_value, current + amount))

    setattr(character, current_attr, new_value)

def damage(character, pool_name: str, amount: int):
    _modify_current(character, pool_name, -amount)

def heal(character, pool_name: str, amount: int):
    _modify_current(character, pool_name, amount)

def spend(character, pool_name: str, amount: int) -> bool:
    current_attr = f"current_{pool_name}"
    current = getattr(character, current_attr)

    if current < amount:
        return False

    _modify_current(character, pool_name, -amount)
    return True


