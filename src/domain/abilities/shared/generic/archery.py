from domain.abilities.builders._job_builder import build_shared_ability


ARCHERY = {
    "name": "Archery",
    "type": "skill",
    "description": "The ability to shoot bows, crossbows, and similar torsion-based weapons.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", ARCHERY, source_type="shared")