from domain.abilities import make_ability
from domain.effects import MultiStatIncrease


def creators_guardians_effect(c):
    level = c.ability_levels.get("Creator's Guardians", 1)
    will = c.attributes.willpower

    bonus = (will + level) // 10

    stats = {
        attr: bonus
        for attr, value in vars(c.attributes).items()
        if value > 0
    }

    return [MultiStatIncrease(stats)]

# Level 1

def register():

    make_ability(
        name="Animus",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
        cost = 10,
        cost_pool = "sanity",
        duration = "10 minutes",
        description = "Turn a touched object into an animi, capable of movement, combat, and simple tasks when ordered by its creator. The greater the size of the object, the more sanity it costs, and the more difficult the roll will be.\n     This skill is a spell, and uses intelligence plus animus for the roll."
    )

    make_ability(
        name="Command Animus",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
        cost = 5,
        cost_pool = "sanity",
        duration = "Instant",
        description = "Allows the caster to issue one command to an animi not in the creator's party. On a success, the animi will complete the command as best it can.\n     This skill is a spell, and uses Intelligence plus Command Animus for the roll. The difficulty is set by the Animi's Willpower roll."
    )

    make_ability(
        name="Creator's Guardians",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
        description = "Enhances animi in the creator's party, boosting all non-zero attributes. The amount is the creator's Willpower and Creator's Guardians skill level, divided by 10.",
        effect_generator=creators_guardians_effect,
    )

    make_ability(
        name="Eye for Detail",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
        cost = 5,
        cost_pool = "sanity",
        duration = "1 minute",
        description = "Allows the animator to examine the status of any animi, golem, or other construct. Also used to analyze any object for animus potential and sanity cost. This is accomplished with an Intelligence plus Eye for Detail roll. The object can make a Willpower roll to resist, with Animi or constructs in a party able to use their creator's Willpower.\n     This skill is a spell.",
    )

    make_ability(
        name="Mend",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
        cost = 5,
        cost_pool = "sanity",
        duration = "1 action",
        description = "Instantly repair the targeted construct or object, restoring a number of HP equal to the Animator's level plus the Mend skill level, divided by two. This is earth-based healing, and can afffecy earth elementals, but not other living creatures.\n     This skill is a spell."
    )
