from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import inspect, skill_check

build_job("Enchanter", [

    {
        "name": "Appraise",
        "cost": 5,
        "cost_pool": "sanity",
        "description": "You can determine the properties of an item. If the item is cursed or illusionary, the GM may roll this secretly to see what you can determine. It is an Intelligence plus Appraise roll. This does not have an experience roll, it instead increases whenver you use it to examine a new item for the first time. This skill is a spell.",
        "duration": "5 minutes",
        "effects": skill_check(
                ability="Appraise",
                stat="intelligence",
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
