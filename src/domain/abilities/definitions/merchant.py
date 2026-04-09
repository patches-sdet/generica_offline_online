from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_derived_buff
from domain.conditions import HAGGLING

build_job("Merchant", [

    {
        "name": "Haggle",
        "cost": 5,
        "cost_pool": "fortune",
        "description": "You always know how to get a good deal. You add this skill to all negotiation skill checks.",
        "duration": "5 minutes",
        "effects": scaled_derived_buff(
                    scale_fn=lambda c: c.ability_levels.get("Haggle", 0),
                    stat={"negotiation": 1}, # This is a placeholder until skills get implemented.
                    condition=HAGGLING,
            ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
