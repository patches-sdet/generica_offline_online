from domain.abilities.builders._job_builder import build_shared_ability

THROW = {
    "name": "Throwing",
    "type": "skill",
    "description": "The ability to accurately and precisely throw an object, either to a friend or at an enemy.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", THROW, source_type="shared")