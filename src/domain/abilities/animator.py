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


def register():

    make_ability(
        name="Animus",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
    )

    make_ability(
        name="Command Animus",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
    )

    make_ability(
        name="Creator's Guardians",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
        effect_generator=creators_guardians_effect,
    )

    make_ability(
        name="Eye for Detail",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
    )

    make_ability(
        name="Mend",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Animator"
            and c.adventure_level >= 1
        ),
    )
