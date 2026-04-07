from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import inspect, skill_check
from domain.conditions import IS_ALLY

build_job("Wizard", [

    {
        "name": "Analyze Magic",
        "cost": 5,
        "cost_pool": "sanity",
        "description": "You can examine the properties of any magical item or spell encountered. This will also list all magical effects active on an individual. This is an Intelligence plus Analyze Magic roll. This skill is a spell.",
        "duration": "1 minute",
        "effects": [
            skill_check(
                ability="Analyze Magic",
                stat="intelligence",
                difficulty=lambda check_ctx, target: target.roll_willpower(),
                on_success=[
                    inspect( # TODO: these reveal fns need to be matched to how equipment and magical effects are implemented, but gets things running for now.
                        reveal_fn=lambda inspect_ctx, target: {
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
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
