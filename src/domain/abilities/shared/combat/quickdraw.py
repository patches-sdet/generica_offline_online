from domain.abilities.factory import make_ability
from domain.content_registry import register_ability
from src.domain.abilities.patterns import action_override

QUICKDRAW = {
    "name": "Quickdraw",
    "type": "skill",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "The character may draw a weapon as part of their attack action without spending additional stamina. This skill has no levels.",
    "effects": lambda ctx, targets: [
        action_override(
            lambda ctx: ctx.allow_draw_as_part_of_attack()
        )
    ],
    "scales_with_level": False,
}