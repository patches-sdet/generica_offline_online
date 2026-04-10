from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
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
        "cost": 5,
        "cost_pool": "moxie",
        "description": (
            "While this skill is active, you are considered to have a job of your choice "
            "if someone investigates your stats. This is a Charisma plus the level of "
            "this skill versus an investigation roll."
        ),
        "effects": [], # This is a conditional effect that will require implementation of the investigation roll and stat concealment mechanics.
        "is_passive": False,
        "is_spell": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Curses
    {
        "name": "Curses",
        "cost": "variable",
        "cost_pool": "fortune",
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
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Enhance Pain
    {
        "name": "Enhance Pain",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Enemies afflicted by this debuff take additional damage equal to your "
            "Cultist level. This is an Intelligence plus the level of this skill versus "
            "their Wisdom roll. Lasts until canceled or dispelled. This skill is a spell."
        ),
        "effects": skill_check(
                ability="Enhance Pain",
                stat="intelligence",
                difficulty=lambda target: target.roll_wisdom(),
                on_success=[
                    conditional_damage(
                        scale_fn=lambda c: c.get_progression_level("adventure", "Cultist", 0),
                        condition=IS_ENEMY,
                    )
                ],
            ),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,        
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    # Occult Eye
    {
        "name": "Occult Eye",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "This skill allows the Cultist to examine an object, area, or being for "
            "traces of occult contamination. This also allows them to read blasphemous "
            "tomes, scrolls, and inscriptions without risking damage."
        ),
        "effects": inspect(
                reveal_fn=lambda target: {
                    "occult_traces": getattr(target, "occult_traces", None),
                    "contamination_level": getattr(target, "contamination_level", None),
                    "blasphemous_text": getattr(target, "blasphemous_text", None),
                }
            ),
        "is_passive": False,
        "is_spell": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "object, area, or being",
        "type": "skill",
    },

    # Transfer Wounds
    {
        "name": "Transfer Wounds",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Transfer wounds from yourself to an enemy. The damage and healing are equal "
            "to your level in this skill. This skill is a spell."
        ),
        "effects": transfer_stat(
                amount_fn=lambda c: c.ability_levels.get("Transfer Wounds", 0),
                condition=IS_ENEMY,
            ),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },
],
source_type="adventure"
)