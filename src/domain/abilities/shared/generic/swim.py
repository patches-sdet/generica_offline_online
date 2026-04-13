from domain.abilities.builders._job_builder import build_shared_ability

SWIM = {
    "name": "Swim",
    "type": "skill",
    "description": "The ability to swim in water deeper than your waist.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", SWIM, source_type="shared")