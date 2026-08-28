def require_single_effect(effects, owner_name: str, ability_name: str, effect_kind: str):
    if len(effects) != 1:
        raise NotImplementedError(
            f"{owner_name}.{ability_name}: expected exactly one {effect_kind} effect spec for now"
        )

    return effects[0]
