from domain.abilities.builders._job_builder import build_shared_ability
from domain.effects.stat_effects import DerivedStatBonus
from domain.effects.conditional import CompositeEffect

FAST_AS_DEATH = {
        "name": "Fast as Death",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 turn per level",
        "description": "For the duration of this skill, you can add 50 to both your initiative and the distance in feet you can run per action. This is a buff.",
        "effects": DerivedStatBonus(
                stat="initiative, movement",
                amount=50,
                source="Fast as Death",
                priority=0
            ),
    }

build_shared_ability("shared.combat", FAST_AS_DEATH)