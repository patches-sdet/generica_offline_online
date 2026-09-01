from domain.abilities.definitions.definitions import AbilityDefinition, AbilityGrant, ActivationSpec, JobDefinition
from domain.abilities.definitions.effects_spec import (
    AbilityLevelBonus,
    ApplyStateSpec,
    ContestedRollSpec, 
    DerivedStatBuffSpec,
    EventValueConditionSpec,
    FlatBonus,
    FollowUpAttackSpec,
    IgnoreTerrainModifierSpec, 
    ModifyNextAttackSpec,
    MovementModifierSpec,
    OnEventSpec,
    PassiveContextModifierSpec,
    PoolCostModifierSpec,
    PoolModifierSpec, 
    ProgressionLevelBonus,
    TimedModifierSpec,
    WeaponRequirementSpec
)

def berserker_job() -> JobDefinition:
    return JobDefinition(
        owner_type="adventure",
        owner_name="Berserker",
        abilities=(

            # LEVEL 1

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
                name="Headbutt",
                kind="skill",
                required_level=1,
                scales_with_level=True,
                description=("The Berserker smashes their head into the enemy. This is a "
                             "Strength + Brawling + Headbutt attack. If it hits, the target must roll Constitution against the Berserker's Headbutt roll or be stunned for 1 round."),
                activation=ActivationSpec(
                    cost=10,
                    cost_pool="hp",
                    duration="1 Attack",
                    target="enemy",
                ),
                effects=(
                    ModifyNextAttackSpec(
                        attack_bonus=(
                            ProgressionLevelBonus(
                                source_type="adventure",
                                source_name="Berserker"
                            ),
                            AbilityLevelBonus(
                                ability_name="Headbutt",
                            ),
                            AbilityLevelBonus(
                                ability_name="Brawling",
                            ),
                            ),
                        ),
                    ContestedRollSpec(
                        attacker_roll="strength + brawling + headbutt",
                        defender_roll="constitution"
                    ),
                    ApplyStateSpec(
                        state="stunned",
                        payload=1
                    ),
                ),
            ),

            AbilityDefinition(
                name="Power From Pain",
                kind="passive",
                required_level=1,
                description=(
                    "Whenever the Berserker loses 10 or more hit points, they gain +1 "
                    "to all strength-based rolls for the next 5 minutes."),
                effects=(
                    OnEventSpec(
                        event_name="hp_lost",
                        condition=EventValueConditionSpec(
                            field_name="amount",
                            operator=">=",
                            value=10,
                        ),
                        effect=ApplyStateSpec(
                            state="power_from_pain_active",
                            payload=(
                                TimedModifierSpec(
                                    duration_minutes=5,
                                    modifier=PassiveContextModifierSpec(
                                    applies_to="skill_roll",
                                    modifier="roll_bonus",
                                    value=(
                                        FlatBonus(
                                            source_name="Power From Pain",
                                            source_type="adventure",
                                            amount=1
                                        ),
                                    ),
                                    requirements=("strength_based",),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),

            # LEVEL 5

            AbilityDefinition(
                name="Reckless Charge",
                kind="skill",
                required_level=5,
                scales_with_level=True,
                description=(
                    "The Berserker doubles their running speed for the turn, ignores "
                    "situational terrain modifiers for the next action, and may immediately "
                    "make a melee attack after moving. That attack gains a bonus equal to "
                    "Reckless Charge's level."
                ),
                activation=ActivationSpec(
                    cost=10,
                    cost_pool="stamina",
                    duration="1 Turn",
                    target="self",
                ),
                effects=(
                    OnEventSpec(
                        event_name="move",
                        effect=ApplyStateSpec(
                            state="reckless_charge_active",
                            payload=(MovementModifierSpec(
                                speed_multiplier=2),
                                IgnoreTerrainModifierSpec(),
                                FollowUpAttackSpec(
                                attack_bonus=(
                                    AbilityLevelBonus("Reckless Charge"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),

            AbilityDefinition(
                name="Wide Swing",
                kind="skill",
                required_level=5,
                description=("The Berserker's next melee attack targets all adjacent enemies. "
                             "Roll once and apply the result to all foes struck. The Berserker "
                             "loses 10 HP per adjacent foe when using this skill. Wide Swing "
                             "adds +1 damage and has no levels."),
                activation=ActivationSpec(
                    cost=10,
                    cost_pool="hp",
                    duration="1 Attack",
                    target="all_adjacent_enemies"
                ),
                effects=(
                    ModifyNextAttackSpec(
                        targets_all_adjacent_enemies=True,
                        single_roll_against_all_targets=True,
                        damage_bonus=(
                            FlatBonus(
                                source_name="Wide Swing",
                                source_type="adventure",
                                amount=1
                            ),
                        ),
                    ),
                    PoolCostModifierSpec(
                        pool="hp",
                        amount=10,
                        per_target=True,
                        target_scope="adjacent_enemies"
                    ),
                ),
            ),

            # LEVEL 10

            AbilityDefinition(
                name="Build Up",
                kind="skill",
                required_level=10,
                scales_with_level=True,
                description=("For each action spent building up, the Berserker's next attack gains "
                             "+10 to hit. The Berserker may spend a number of actions equal to this "
                             "skill's level. The effect lasts 1 minute or until used."),
                activation=ActivationSpec(
                    cost=20,
                    cost_pool="moxie",
                    duration="1 minute or until used",
                    target="self"
                ),
                effects=(
                    ApplyStateSpec(
                        state="build_up",
                        payload=(
                            AbilityLevelBonus(
                                ability_name="Build Up",
                                multiplier=10
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
                    ),
                ),
            ),

            # LEVEL 15

            AbilityDefinition(
                name="Two-Handed Specialist",
                kind="passive",
                required_level=15,
                scales_with_level=True,
                description=("While using a two-handed weapon, the Berserker gains +1 to attack rolls "
                             "for every level of this skill."),
                activation=ActivationSpec(duration="Passive Constant", target="self"),
                effects=(
                    PassiveContextModifierSpec(
                        applies_to="skill_roll",
                        modifier="roll_bonus",
                        value=(
                            AbilityLevelBonus(
                                ability_name="Two-Handed Specialist"
                            ),
                        ),
                    ),
                    WeaponRequirementSpec(
                        style="two-handed",
                        wielding_mode="two-handed",
                    ),
                ),
            ),

            # LEVEL 20

            AbilityDefinition(
                name="Iron Skin",
                kind="skill",
                required_level=20,
                scales_with_level=True,
                description=("The Berserker hardens their muscles like armor, gaining a buff to Armor "
                             "equal to the level of this skill."),
                activation=ActivationSpec(
                    cost=50,
                    cost_pool="stamina",
                    duration="1 minute",
                    target="self"
                ),
                effects=(
                    DerivedStatBuffSpec(
                        stat="armor",
                        amount=(
                            AbilityLevelBonus(
                                ability_name="Iron Skin"
                            ),
                        ),
                    ),
                ),
            ),

            AbilityDefinition(
                name="The Bigger They Are...",
                kind="skill",
                required_level=20,
                description=("The Berserker's next attack ignores armor equal to twice their Berserker level. "
                             "This skill may only be used against a foe of equal or larger size. This skill has no levels."),
                activation=ActivationSpec(
                    cost=25,
                    cost_pool="moxie",
                    duration="1 Attack",
                    target="enemy"
                ),
                effects=(
                    ModifyNextAttackSpec(
                        ignore_armor=(
                            ProgressionLevelBonus(
                                source_type="adventure",
                                source_name="Berserker",
                                multiplier=2
                            ),
                        ),
                        relative_target_sizes=("equal", "larger"),
                        ),
                    ),
                ),

            # LEVEL 25

            AbilityDefinition(
                name="All You Need is Kill",
                kind="skill",
                required_level=25,
                scales_with_level=True,
                description=(
                    "Whenever the Berserker knocks a foe unconscious or kills them, "
                    "they may pay 25 Moxie to regain hit points equal to this skill's level."
                ),
                activation=ActivationSpec(
                    cost=25,
                    cost_pool="moxie",
                    duration="Instant",
                    target="self",
                ),
                effects=(
                    OnEventSpec(
                        event_name="target_defeated",
                        condition=EventValueConditionSpec(
                            field_name="outcome",
                            operator="in",
                            value=("unconscious", "dead"),
                        ),
                        effect=PoolModifierSpec(
                            pool="hp",
                            amount=(AbilityLevelBonus("All You Need is Kill"),),
                        ),
                    ),
                ),
            ),

            AbilityDefinition(
                name="Two-Handed Titan",
                kind="passive",
                required_level=25,
                description=("The Berserker may wield a two-handed weapon as though it were one-handed. "
                            "They also reduce the stamina damage multiplier of any weapon they wield by 2 multiples, "
                            "to a minimum of x1. This skill has no levels."),
                activation=ActivationSpec(duration="Passive Constant", target="self"),
                effects=(
                    ApplyStateSpec(
                        state="wield_two_handed_as_one_handed",
                    ),
                    PassiveContextModifierSpec(
                        applies_to="weapon_use",
                        modifier="pool_cost",
                        value=(
                            FlatBonus(
                                source_name="Two-Handed Titan",
                                source_type="adventure",
                                amount=-2
                            ),
                        ),
                    ),
                ),
            ),
        ),

        grants=(
            AbilityGrant(
                name="Growl",
                required_level=1
            ),
            AbilityGrant(
                name="Rage",
                required_level=1
            ),
            AbilityGrant(
                name="Toughness",
                required_level=5
            ),
            AbilityGrant(
                name="Fast as Death",
                required_level=15
            ),
        ),
    )