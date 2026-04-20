from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

GET_THAT_GUY = {
        "name": "Get That Guy!",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "The Bandit singles out one target for punishment. Every bastard who attacks that target "
            "gains a bonus to attack rolls equal to the Bandit's level."
        ),
        "duration": "1 turn per level",
        "effects": apply_state(
            "get_that_guy",
            value_fn=lambda source: {
                "duration_turns": _ability_level(source, "Get That Guy!"),
                "attack_bonus": _bandit_level(source),
                "applies_to": "bastards_against_marked_target",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    }

build_shared_ability("shared.combat", GET_THAT_GUY, source_type="shared")