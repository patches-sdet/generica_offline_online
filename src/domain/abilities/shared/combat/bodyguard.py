from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

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
                "duration_turns": _ability_level(source, "Bodyguard"),
                "protect_target": True,
                "target_damage_multiplier": 0.5,
                "guardian_takes_remaining_damage": True,
                "transferred_damage_bypasses_defenses": True,
                "transferred_damage_cannot_be_reduced": True,
                "no_bodyguard_chains": True,
                "source_ability": "Bodyguard",
            },
        ),
        "required_level": 15,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    }

build_shared_ability("shared.combat", BODYGUARD, source_type="shared")