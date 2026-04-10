from domain.abilities.builders._job_builder import build_job

build_job("Crossbreed", [
    {"grant": "Human Blood", "required_level": 1},
    {"grant": "Beast Blood", "required_level": 1}
],
source_type="race",
)