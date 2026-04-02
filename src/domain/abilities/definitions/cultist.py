from domain.abilities.definitions._job_builder import build_job
from domain.abilities.patterns import (
    buff,
    conditional_damage,
    transfer_stat,
    scaled_derived_buff,
    skill_check,
    inspect,
)
from domain.conditions import IS_ENEMY


build_job("Cultist", [

    # Conceal Status
    {
        "name": "Conceal Status",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "target": "self",
        "description": (
            "While this skill is active, you are considered to have a job of your choice "
            "if someone investigates your stats. This is a Charisma plus the level of "
            "this skill versus an investigation roll."
        ),
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Cultist", 0),
                stats={"any": 1},  # placeholder until inspection-disguise system exists
            )
        ],
    },

    # Curses
    {
        "name": "Curses",
        "type": "skill",
        "cost": "variable",
        "cost_pool": "fortune",
        "target": "enemy",
        "description": (
            "Inflict a curse on an enemy, reducing a chosen derived stat by an amount "
            "equal to the Fortune spent. This effect lasts until canceled or dispelled. "
            "This skill is a spell."
        ),
        "effects": lambda ctx: [
            scaled_derived_buff(
                stat=ctx.chosen_stat,
                scale_fn=lambda c: ctx.spent_amount,
                condition=IS_ENEMY,
            )
        ],
    },

    # Enhance Pain
    {
        "name": "Enhance Pain",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "target": "enemy",
        "description": (
            "Enemies afflicted by this debuff take additional damage equal to your "
            "Cultist level. This is an Intelligence plus the level of this skill versus "
            "their Wisdom roll. Lasts until canceled or dispelled. This skill is a spell."
        ),
        "effects": lambda ctx: [
            skill_check(
                ability="Enhance Pain",
                stat="intelligence",
                difficulty=lambda check_ctx, target: target.roll_wisdom(),
                on_success=[
                    conditional_damage(
                        scale_fn=lambda c: c.get_progression_level("adventure", "Cultist", 0),
                    )
                ],
            )
        ],
    },

    # Occult Eye
    {
        "name": "Occult Eye",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "target": "self",
        "description": (
            "This skill allows the Cultist to examine an object, area, or being for "
            "traces of occult contamination. This also allows them to read blasphemous "
            "tomes, scrolls, and inscriptions without risking damage."
        ),
        "effects": lambda ctx: [
            inspect(
                reveal_fn=lambda inspect_ctx, target: {
                    "occult_traces": getattr(target, "occult_traces", None),
                    "contamination_level": getattr(target, "contamination_level", None),
                    "blasphemous_text": getattr(target, "blasphemous_text", None),
                }
            )
        ],
    },

    # Transfer Wounds
    {
        "name": "Transfer Wounds",
        "type": "skill",
        "cost": 10,
        "cost_pool": "fortune",
        "target": "enemy",
        "description": (
            "Transfer wounds from yourself to an enemy. The damage and healing are equal "
            "to your level in this skill. This skill is a spell."
        ),
        "effects": lambda ctx: [
            transfer_stat(
                amount_fn=lambda c, effect_ctx: c.ability_levels.get("Transfer Wounds", 0),
                condition=IS_ENEMY,
            )
        ],
    },

])