from domain.abilities.builders._job_builder import build_shared_ability

LOCKPICKING = {
    "name": "Lockpicking",
    "type": "skill",
    "description": "The ability to pick locks on chests and doors.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", LOCKPICKING, source_type="shared")