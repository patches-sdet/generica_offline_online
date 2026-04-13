from domain.abilities.builders._job_builder import build_shared_ability

AXES = {
    "name": "Axes & Choppas",
    "type": "skill",
    "description": "The ability to use axes effectively.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", AXES, source_type="shared")