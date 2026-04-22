from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state
from domain.abilities import ability_level


BODYGUARD = {
    "name": "Bodyguard",
    "cost": 25,
    "cost_pool": "stamina",
    "description": (
        "Choose a target. While active, damage they take is halved, and you take the remaining half. "
        "The transferred damage bypasses defenses and cannot be reduced further."
    ),
    "duration": "1 Turn per Skill Level",
    "effects": apply_state(
        "bodyguard_active",
        value_fn=lambda source: {
            "active": True,
            "duration_turns": ability_level(source, "Bodyguard"),
            "target_required": True,
            "single_protected_target": True,
            "protected_target_takes_half_damage": True,
            "guardian_takes_remaining_damage": True,
            "transferred_damage_bypasses_defenses": True,
            "transferred_damage_cannot_be_reduced": True,
            "no_bodyguard_chains": True,
            "source_ability": "Bodyguard",
        },
    ),
    "scales_with_level": True,
    "target": "ally",
    "type": "skill",
}

build_shared_ability("shared.combat", BODYGUARD, source_type="shared")