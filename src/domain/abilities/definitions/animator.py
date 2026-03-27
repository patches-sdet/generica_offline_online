from domain.abilities import make_ability
from domain.abilities.patterns import (
    heal,
    buff,
    summon,
    control,
    inspect,
    on_success,
    filtered,
    skill_check
)

from domain.conditions import (
    IS_CONSTRUCT,
    IS_OBJECT,
    NOT_IN_PARTY,
)

# =========================================================
# Animus — Summon / Create Animi
# =========================================================

def animus_execute(caster, targets):
    return [
        summon(
            factory_fn=lambda caster, obj: create_animi_from_object(
                caster=caster,
                obj=obj,
                power=(
                    caster.attributes.intelligence +
                    caster.skills.get("Animus", 0)
                )
            ),
            condition=IS_OBJECT,
        )
    ]


# =========================================================
# Command Animus — Control External Construct
# =========================================================

def command_animus_execute(caster, targets):
    return [
        filtered(
            skill_check(
                skill="Command Animus",
                difficulty=lambda ctx, target: target.roll_willpower(),
                on_success=SetControllerEffect(duration="1 command"),
                    success_condition=lambda ctx, target: True,  # already gated above
                ),
            condition=lambda ctx, target: (
                IS_CONSTRUCT(ctx, target) and NOT_IN_PARTY(ctx.source, target)
            ),
        )
    ]


# =========================================================
# Creator's Guardians — Passive Aura Buff
# =========================================================

def creators_guardians_effects(character):
    return [
        buff(
            scale_fn=lambda c: (
                c.attributes.willpower +
                c.ability_levels.get("Creator's Guardians", 0)
            ) // 10,
            stats={
                "strength": 1,
                "dexterity": 1,
                # TODO: expand to all non-zero attributes
            },
            condition=IS_CONSTRUCT,
        )
    ]


# =========================================================
# Eye for Detail — Inspect / Analyze
# =========================================================

def eye_for_detail_execute(caster, targets):
    return [
        inspect(
            reveal_fn=lambda caster, target: {
                "type": getattr(target, "type", None),
                "hp": getattr(target, "hp", None),
                "attributes": getattr(target, "attributes", None),
                "animus_potential": estimate_animus_value(target),
            },
            condition=lambda ctx, target: (
                IS_CONSTRUCT(ctx, target) or IS_OBJECT(ctx, target)
            ),
        )
    ]


# =========================================================
# Mend — Construct Healing
# =========================================================

def mend_execute(caster, targets):
    return [
        heal(
            scale_fn=lambda c: (
                c.get_adventure_level_by_name("Animator") +
                c.skills.get("Mend", 0)
            ) // 2,
            condition=IS_CONSTRUCT,
        )
    ]


# =========================================================
# Registration
# =========================================================

def register():

    make_ability(
        name="Animus",
        unlock_condition=lambda c: (
            c.has_adventure_job("Animator")
            and c.get_adventure_level_by_name("Animator") >= 1
        ),
        execute=animus_execute,
        cost=10,
        cost_pool="sanity",
        duration="10 minutes",
        description="Turn a touched object into an animi, capable of movement, combat, and simple tasks when ordered by its creator. The greater the size of the object, the more sanity it costs, and the more difficult the roll will be.\n     This skill is a spell, and uses intelligence plus animus for the roll.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Command Animus",
        unlock_condition=lambda c: (
            c.has_adventure_job("Animator")
            and c.get_adventure_level_by_name("Animator") >= 1
        ),
        execute=command_animus_execute,
        cost=5,
        cost_pool="sanity",
        duration="Instant",
        description="Allows the caster to issue one command to an animi not in the creator's party. On a success, the animi will complete the command as best it can.\n     This skill is a spell, and uses Intelligence plus Command Animus for the roll. The difficulty is set by the Animi's Willpower roll.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Creator's Guardians",
        unlock_condition=lambda c: (
            c.has_adventure_job("Animator")
            and c.get_adventure_level_by_name("Animator") >= 1
        ),
        effect_generator=creators_guardians_effects,
        duration="Passive Constant",
        description="Enhances animi in the creator's party, boosting all non-zero attributes. The amount is the creator's Willpower and Creator's Guardians skill level, divided by 10.",
        is_passive=True,
        is_skill=False,
    )

    make_ability(
        name="Eye for Detail",
        unlock_condition=lambda c: (
            c.has_adventure_job("Animator")
            and c.get_adventure_level_by_name("Animator") >= 1
        ),
        execute=eye_for_detail_execute,
        cost=5,
        cost_pool="sanity",
        duration="1 minute",
        description="Allows the animator to examine the status of any animi, golem, or other construct. Also used to analyze any object for animus potential and sanity cost. This is accomplished with an Intelligence plus Eye for Detail roll. The object can make a Willpower roll to resist, with Animi or constructs in a party able to use their creator's Willpower.\n     This skill is a spell.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Mend",
        unlock_condition=lambda c: (
            c.has_adventure_job("Animator")
            and c.get_adventure_level_by_name("Animator") >= 1
        ),
        execute=mend_execute,
        cost=5,
        cost_pool="sanity",
        duration="1 action",
        description="Instantly repair the targeted construct or object, restoring a number of HP equal to the Animator's level plus the Mend skill level, divided by two. This is earth-based healing, and can afffecy earth elementals, but not other living creatures.\n     This skill is a spell.",
        is_passive=False,
        is_skill=True,
    )
