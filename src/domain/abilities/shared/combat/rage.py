from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state, scaled_derived_buff, scaled_stat_buff
from domain.effects.conditional import CompositeEffect

RAGE = {
        "name": "Rage",
        "cost": 5,
        "cost_pool": "moxie",
        "description": "You would like to RAGE! While raging, you cannot use ranged attacks or spells, and you suffer a perception debuff equal to your Berserker level. Additionally, you may add your Berserker level to all other rolls. This is an increase, not a buff. You may not rage for more turns than you have levels in this skill.",
        "duration": "1 Turn/level",
            "effects": CompositeEffect([
            apply_state("raging"),
            apply_state("cannot_use_ranged_attacks"),
            apply_state("cannot_cast_spells"),
            scaled_stat_buff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Berserker", 0),
                stats={"perception": -1},
            ),
            scaled_derived_buff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Berserker", 0),
                stat="all_rolls",
                condition=lambda c: "raging" in getattr(c.source, "states", {}),
                ),
            ],
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    }

build_shared_ability("shared.combat", RAGE)