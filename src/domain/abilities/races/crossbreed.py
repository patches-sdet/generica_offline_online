from domain.abilities.builders._job_builder import build_job

build_job("Crossbreed", [
    {"grant": "Human Blood", "required_level": 1},

    {
        "name": "Mixed Blood 1",
        "required_level": 1,
        "type": "passive",
        "description": "Choose one level 1 racial job skill from your other parent's race and add it to your skill list. Then remove this skill from your list.",
        "effects": [], # This is a complicated effect that might need a custom pattern or effect.
        "scales_with_level": False,
    },
])