from domain.abilities.builders._job_builder import build_job

build_job("Raccant", [
    {"grant": "Forage", "required_level": 1},
    {"grant": "Darkspawn", "required_level": 1},
    {"grant": "Sturdy", "required_level": 1}
],
source_type="race",
)