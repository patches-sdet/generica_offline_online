from domain.abilities.builders._job_builder import build_shared_ability

FLIGHT = {
    "name": "Flight",
    "type": "skill",
    "description": "The ability to maneuver in midair, or falling gracefully without dying.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", FLIGHT, source_type="shared")