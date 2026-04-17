from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

CANNON_FODDER = {
    "name": "Cannon Fodder",
    "cost": 20,
    "cost_pool": "sanity",
    "description": (
        "If the user is struck and has a nearby ally or subordinate within arm's reach, "
        "they may attempt to shunt the attack to that target instead. "
        "This is resisted by the chosen target's Perception."
    ),
    "duration": "Instant",
    "effects": apply_state(
        "cannon_fodder_ready",
        value_fn=lambda source: {
            "active": True,
            "requires_nearby_redirect_target": True,
            "contest_stat": "wisdom",
            "resist_stat": "perception",
        },
    ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "scales_with_level": False,
    "target": "self",
    "type": "skill",
}

build_shared_ability("shared.combat", CANNON_FODDER)