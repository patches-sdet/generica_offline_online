from domain.abilities.builders._job_builder import build_shared_ability

GUNS = {
    "name": "Guns",
    "type": "skill",
    "description": "The ability to use firearms and other gun-based weapons.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", GUNS, source_type="shared")