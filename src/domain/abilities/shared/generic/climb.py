from domain.abilities.builders._job_builder import build_shared_ability

CLIMB = {
    "name": "Climb",
    "type": "skill",
    "description": "The ability to climb and navigate treacherous slopes.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", CLIMB, source_type="shared")