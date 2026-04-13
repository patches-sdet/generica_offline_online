from domain.abilities.builders._job_builder import build_shared_ability

STEALTH = {
    "name": "Stealth",
    "type": "skill",
    "description": "The ability to move undetected.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", STEALTH, source_type="shared")