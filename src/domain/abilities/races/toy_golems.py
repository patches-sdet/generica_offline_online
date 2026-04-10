from domain.abilities.builders._job_builder import build_job

build_job("Toy Golem", [
    {"grant": "Adorable", "required_level": 1},
    {"grant": "Golem Body", "required_level": 1},
    {"grant": "Magic Resistance", "required_level": 1},
    # {"grant": "Plush Form"}, This probably can stay commented out; the way the creator is built handles this skill before the skill would be assigned and need to be "selected from options".

    {
        "name": "Gift of Sapience",
        "required_level": 1,
        "type": "passive",
        "description": "Your toy golem is imbued with a spark of sapience, granting it all attributes and can think and learn.",
        "effects": [],
    },
],
source_type="race",
)