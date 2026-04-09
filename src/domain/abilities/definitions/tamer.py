from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import inspect, skill_check

build_job("Tamer", [

    {
        "name": "Analyze Monster",
        "cost": 5,
        "cost_pool": "fortune",
        "description": "You can examine a beast or monster's status screen. This is a Perception plus Analyze Monster roll against the target's Willpower.",
        "duration": "5 minutes",
        "effects": skill_check(
                ability="Analyze Monster",
                stat="perception",
                difficulty=lambda target: target.roll_willpower(),
                on_success=[
                    inspect(
                        reveal_fn=lambda target: {
                            "type": getattr(target, "type", None),
                            "hp": getattr(target, "hp", None),
                            "attributes": getattr(target, "attributes", None),
                            "adventure_jobs": getattr(target, "adventure_jobs", None),
                            "adventure_levels": getattr(target, "adventure_levels", None),
                            "profession_jobs": getattr(target, "profession_jobs", None),
                            "profession_levels": getattr(target, "profession_levels", None),
                        },
                    )
                ],
            ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
