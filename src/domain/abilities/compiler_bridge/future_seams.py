from domain.abilities.definitions.effects_spec import ApplyStateSpec, OnEventSpec


def compile_event_effects(effects, owner_name: str, ability_name: str):
    """Reserved phase 6 seam for event-driven ability compilation."""
    raise NotImplementedError(
        f"{owner_name}.{ability_name}: event-driven compilation is reserved for phase 6"
    )


def compile_state_effects(effects, owner_name: str, ability_name: str):
    """Reserved phase 6 seam for state-driven ability compilation."""
    raise NotImplementedError(
        f"{owner_name}.{ability_name}: state-driven compilation is reserved for phase 6"
    )


PHASE_6_RESERVED_EFFECT_SPECS = (
    ApplyStateSpec,
    OnEventSpec,
)
