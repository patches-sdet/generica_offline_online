from domain.abilities.builders._job_builder import build_shared_ability

RIDING = {
    "name": "Riding",
    "type": "skill",
    "description": "The ability to ride mounts.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", RIDING, source_type="shared")