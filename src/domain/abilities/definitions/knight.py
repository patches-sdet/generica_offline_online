from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import heal_moxie
from domain.conditions import IS_ALLY

build_job("Knight", [

    {
        "name": "Rally Troops",
        "cost": 10,
        "cost_pool": "moxie",
        "description": "You can rally your allies with a few encouraging words. This will heal all allies that can hear you for a small amount of moxie equal to your level in this skill.",
        "duration": "1 Action",
        "effects": heal_moxie(
                scale_fn=lambda ctx: ctx["user"].get_skill_level("Rally Troops"),
                condition=IS_ALLY,
            ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "allies",
        "type": "passive",
    },
],
source_type="adventure"
)