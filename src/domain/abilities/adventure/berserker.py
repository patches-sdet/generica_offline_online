from domain.abilities.definitions.definitions import AbilityDefinition, ActivationSpec, JobDefinition
from domain.abilities.definitions.effects_spec import (
    AbilityLevelBonus, 
    DerivedStatBuffSpec, 
    ModifyNextAttackSpec, 
    ProgressionLevelBonus
)

def berserker_job() -> JobDefinition:
    return JobDefinition(
        owner_type="adventure",
        owner_name="Berserker",
        abilities=(
            AbilityDefinition(
                name="Furious Strike",
                kind="skill",
                required_level=1,
                scales_with_level=True,
                description=("Your next attack inflicts additional damage equal to your Berserker level "
                "plus the level of this skill. The bonus damage is wasted if the attack misses."
            ),
                activation=ActivationSpec(
                    cost=10,
                    cost_pool="hp",
                    duration="1 Attack",
                    target="enemy",
                ),
                effects=(
                    ModifyNextAttackSpec(
                        damage_bonus=(
                            ProgressionLevelBonus(
                                source_type="adventure",
                                source_name="Berserker",
                            ),
                            AbilityLevelBonus(
                                ability_name="Furious Strike",
                            ),
                        ),
                    ),
                ),
            ),
            AbilityDefinition(
                name = "Tough as Leather",
                kind = "passive",
                required_level = 10,
                description = ("The Berserker's body hardens with conditioning. Increase Endurance by "
                                "their Berserker level."),
                activation = ActivationSpec(duration = "Passive Constant", target = "self"),
                effects = (
                    DerivedStatBuffSpec(
                        stat = "endurance", 
                        amount = (
                            ProgressionLevelBonus(
                                source_type = "adventure", 
                                source_name = "Berserker"
                        ),
                    ),
                ),),
            ),
        ),
    )