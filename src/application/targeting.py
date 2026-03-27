def resolve_targets(caster, ability):
    target_type = getattr(ability, "target_type", "self")

    if target_type == "self":
        return [caster]

    if target_type == "party":
        return getattr(caster, "party", [caster])

    if target_type == "allies":
        return getattr(caster, "party", [caster])

    if target_type == "enemies":
        return getattr(caster, "enemies", [])

    if target_type == "all":
        return getattr(caster, "party", []) + getattr(caster, "enemies", [])

    # fallback
    return [caster]
