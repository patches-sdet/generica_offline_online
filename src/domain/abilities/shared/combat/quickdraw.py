from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import action_override

QUICKDRAW = {
    "name": "Quickdraw",
    "type": "skill",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "Spend 5 stamina to draw a weapon as part of your attack action without spending a separate action. This ability has no levels.",
    "effects": lambda ctx: [
        action_override(
            lambda ctx: (ctx.allow_draw_as_part_of_attack())
        )
    ],
    "scales_with_level": False,
}

build_shared_ability("shared.combat", QUICKDRAW, source_type="adventure")