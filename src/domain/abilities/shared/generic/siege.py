from domain.abilities.builders._job_builder import build_shared_ability

SIEGE = {
    "name": "Siege",
    "type": "skill",
    "description": "The ability to operate siege engines and other large-scale military equipment.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", SIEGE, source_type="shared")