from domain.abilities.builders._job_builder import build_job

build_job("Cat", [
    {"grant": "Animalistic Interface", "required_level": 1},
    {"grant": "Beast", "required_level": 1},
    {"grant": "Claw Swipes", "required_level": 1},
    {"grant": "Groom", "required_level": 1},
    {"grant": "Nine Lives", "required_level": 1},
    {"grant": "Scents and Sensibility", "required_level": 1}
],
source_type="race",
)