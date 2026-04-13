from domain.abilities.builders._job_builder import build_shared_ability

BRAWLING = {
    "name": "Brawling",
    "type": "skill",
    "description": "The ability to fight unarmed or with natural weaponry.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", BRAWLING, source_type="shared")