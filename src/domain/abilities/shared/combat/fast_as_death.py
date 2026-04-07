from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import buff

FAST_AS_DEATH = {
        "name": "Fast as Death",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 turn per level",
        "description": "For the duration of this skill, you can add 50 to both your initiative and the distance in feet you can run per action. This is a buff.",
        "effects": lambda ctx: [
            buff(
                stats={
                    "initiative": 50,
                    "movement": 50,
                },
            ),
        ],
    }

build_shared_ability("shared.combat", FAST_AS_DEATH)