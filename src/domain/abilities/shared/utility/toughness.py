from domain.abilities.builders._job_builder import build_shared_ability

TOUGHNESS = {
    "name": "Toughness",
    "type": "passive",
    "description": (
        "Increases Maximum HP by 2 per rank. "
        "This skill ranks up when a single hit deals more damage than "
        "Constitution + current Toughness rank."
    ),
    "effects": [],
    "is_passive": True,
    "is_skill": True,
    "scales_with_level": True,
}

build_shared_ability("shared.utility", TOUGHNESS, source_type="shared")