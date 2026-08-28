from domain.abilities.compiler_bridge.active import compile_active_effects
from domain.abilities.compiler_bridge.future_seams import compile_event_effects, compile_state_effects
from domain.abilities.compiler_bridge.passive import compile_passive_effects
from domain.abilities.definitions.effects_spec import ApplyStateSpec, OnEventSpec


def _contains_effect_type(effects, effect_type: type[object]) -> bool:
    return any(isinstance(effect, effect_type) for effect in effects)


def dispatch_effect_compiler(defn, owner_name: str):
    if defn.kind == "passive":
        if _contains_effect_type(defn.effects, ApplyStateSpec):
            return lambda effects: compile_state_effects(effects, owner_name, defn.name)
        return lambda effects: compile_passive_effects(effects, owner_name, defn.name)

    if _contains_effect_type(defn.effects, OnEventSpec):
        return lambda effects: compile_event_effects(effects, owner_name, defn.name)

    return lambda effects: compile_active_effects(effects, owner_name, defn.name)
