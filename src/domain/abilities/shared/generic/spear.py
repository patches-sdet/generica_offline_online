from domain.abilities.builders._job_builder import build_shared_ability

SPEAR = {
    "name": "Spears",
    "type": "skill",
    "description": "The ability to use spears and other pole-based weapons.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", SPEAR, source_type="shared")