from domain.abilities.builders._job_builder import build_shared_ability

DAGGER = {
    "name": "Dagger",
    "type": "skill",
    "description": "This covers the use of all short bladed knives and daggers in combat.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", DAGGER, source_type="shared")