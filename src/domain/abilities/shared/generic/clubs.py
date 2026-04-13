from domain.abilities.builders._job_builder import build_shared_ability

CLUBS = {
    "name": "Clubs & Maces",
    "type": "skill",
    "description": "The ability to use all kinds of bludgeoning weapons, including staves.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", CLUBS, source_type="shared")