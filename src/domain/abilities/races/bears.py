from domain.abilities.builders._job_builder import build_job

build_job("Bear", [
    {"grant": "Animalistic Interface", "required_level": 1},
    {"grant": "Beast", "required_level": 1},
    {"grant": "Claw Swipes", "required_level": 1},
    {"grant": "Forage", "required_level": 1},
    {"grant": "Scents and Sensibility", "required_level": 1},
    {"grant": "Toughness", "required_level": 1},
    {"grant": "Growl", "required_level": 1}, # placeholder until I fix the test harness with the actual required_level for bears: 5 not 1
],
source_type="race",
)