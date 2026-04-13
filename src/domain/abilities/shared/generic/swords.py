from domain.abilities.builders._job_builder import build_shared_ability

SWORDS = {
    "name": "Swords",
    "type": "skill",
    "description": "Proficiency with various types of swords.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", SWORDS, source_type="shared")