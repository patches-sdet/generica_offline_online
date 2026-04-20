from domain.abilities.builders._job_builder import build_job

# Narrative Unlock conditions: 
# requires Cultist 25, Knight 25. The rest is narrative and can be adjusted as needed.

build_job("Demon Knight", [

     {"grant": "Staredown", "required_level": 1},
],
source_type="advanced",
)