from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state


POMMEL_STRIKE = {
    "name": "Pommel Strike",
    "cost": 15,
    "cost_pool": "stamina",
    "description": (
        "While this skill is active, you may use the nonlethal option, and foes struck in such a manner "
        "cannot roll Constitution to boost their Endurance against your strikes. Pommel Strike also adds "
        "its level to all stamina damage inflicted this way."
    ),
    "duration": "1 Minute",
    "effects": apply_state(
        "pommel_strike_active",
        value_fn=lambda source: {
            "active": True,
            "duration_minutes": 1,
            "nonlethal_enabled": True,
            "disable_constitution_to_endurance_boost": True,
            "bonus_stamina_damage": source.get_ability_effective_level("Pommel Strike"),
            "source_ability": "Pommel Strike",
        },
    ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "scales_with_level": True,
    "target": "self",
    "type": "skill",
}

build_shared_ability("shared.combat", POMMEL_STRIKE, source_type="adventure")