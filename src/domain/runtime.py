from domain.calculations import calculate_pools

def _get_current_attr(pool_name: str) -> str:
    return f"current_{pool_name}"

def _validate_pool(character, pool_name: str, amount: int):
    attr = _get_current_attr(pool_name)

    if not hasattr(character, attr):
        raise ValueError(f"Invalid pool: {pool_name}")

def _modify_current(character, pool_name: str, amount: int):
    _validate_pool(character, pool_name, amount)

    if amount == 0:
        return

    current_attr = _get_current_attr(pool_name)
    current = getattr(character, current_attr)

    max_value = getattr(calculate_pools(character), pool_name)[1]

    new_value = max(0, min(max_value, current + amount))
    setattr(character, current_attr, new_value)

    # Resource Management and Operations

def damage(character, pool_name: str, amount: int):
    if amount < 0:
        raise ValueError("Damage amount cannot be negative")

    _modify_current(character, pool_name, -amount)

def heal(character, pool_name: str, amount: int):
    if amount < 0:
        raise ValueError("Heal amount cannot be negative")

    _modify_current(character, pool_name, amount)

def spend(character, pool_name: str, amount: int) -> bool:
    _validate_pool(character, pool_name, amount)

    if amount < 0:
        raise ValueError("Spend amount cannot be negative")


    current_attr = _get_current_attr(pool_name)
    current = getattr(character, current_attr)

    if current < amount:
        return False

    _modify_current(character, pool_name, -amount)
    return True

def execute_ability(character, ability_name: str):
    ability = next(
        (a for a in character.abilities if a.name == ability_name),
        None
    )

    if not ability:
        raise ValueError(f"Ability '{ability_name}' not found")

    # Handle cost automatically
    if ability.cost:
        pool = getattr(ability, "cost_pool", "fortune")

        success = spend(character, ability.cost_pool, ability.cost)

        if not success:
            raise ValueError(f"Not enough {ability.cost_pool.capitalize()}")

    # Run ability logic
    if ability.execute:
        ability.execute(character)
