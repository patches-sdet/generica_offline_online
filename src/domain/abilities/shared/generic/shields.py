from domain.abilities.builders._job_builder import build_shared_ability

SHIELDS = {
    "name": "Shields",
    "type": "skill",
    "description": "The ability to use shields for offense.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", SHIELDS, source_type="shared")