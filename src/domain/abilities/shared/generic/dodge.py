from domain.abilities.builders._job_builder import build_shared_ability

DODGE = {
    "name": "Dodge",
    "type": "skill",
    "description": "The ability to avoid incoming attacks.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", DODGE, source_type="shared")