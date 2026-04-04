from domain.abilities.builders._job_builder import build_job

build_job("Toy Golem", [
    {"grant": "Adorable"},
    {"grant": "Golem Body"},
    {"grant": "Magic Resistance"},
    {"grant": "Plush Form"},

    {
        "name": "Gift of Sapience",
        "type": "passive",
        "description": "Your toy golem is imbued with a spark of sapience, granting it all attributes and can think and learn.",
        "effects": [],
    },

])