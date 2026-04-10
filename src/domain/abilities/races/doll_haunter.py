from domain.abilities.builders._job_builder import build_job

build_job("Doll Haunter", [
    {"grant": "Adorable", "required_level": 1},
    {"grant": "Haunting Spirit (Undead)", "required_level": 1},
    {"grant": "Golem Body", "required_level": 1},
    {"grant": "Magic Resistance", "required_level": 1},
    # {"grant": "Plush Form"}, same as Toy Golem, the character creator handles this skill before the skill would be assigned and need to be "selected from options".
],
source_type="race",
)