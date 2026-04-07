from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import buff

POISON_RESISTANCE = {
    "name": "Poison Resistance",
    "type": "passive",
    "description": "You may make Constitution rolls to resist poison and add your level in this skill to the roll.",
    "effects": lambda ctx: [
        buff(
            name="Poison Resistance",
            stat="constitution",
            amount=lambda ctx: ctx.source.roll_constitution(),
            difficulty= [],
        )
    ],
    "is_passive": True,
    "is_skill": True,
    "scales_with_level": True,
}

build_shared_ability("shared.utility", POISON_RESISTANCE)