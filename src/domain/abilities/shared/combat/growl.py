from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import skill_check, moxie_damage
from domain.conditions import IS_ENEMY

GROWL = {
        "name": "Growl",
        "type": "skill",
        "cost": 10,
        "cost_pool": "moxie",
        "duration": "1 Attack",
        "description": "Growl at an enemy, inflicting moxie damage. This is a Charisma plus Growl skill roll against the target's Willpower.",
        "target": "enemy",
        "effects": skill_check(
                ability="Growl",
                stat="charisma",
                difficulty=lambda target: target.roll_willpower(),
                on_success=[
                    moxie_damage(
                        scale_fn=lambda c: c.ability_levels.get("Growl", 0),
                        condition=IS_ENEMY,
                    )
                ],
            ),
        "scales_with_level": True,
    }

build_shared_ability("shared.combat", GROWL)