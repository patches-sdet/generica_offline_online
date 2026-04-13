from domain.abilities.builders._job_builder import build_shared_ability

FISHING = {
    "name": "Fishing",
    "type": "skill",
    "description": "The ability to catch fish and other aquatic creatures with a net or pole.",
    "target": "self",
    "effects": [],
    "scales_with_level": True,
}

build_shared_ability("generic", FISHING, source_type="shared")