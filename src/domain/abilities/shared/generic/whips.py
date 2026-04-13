from domain.abilities.builders._job_builder import build_shared_ability

WHIP = {
    "name": "Whips & Flails",
    "type": "skill",
    "description": "The ability to use whips and other flexible weapons, including nets for combat.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", WHIP, source_type="shared")