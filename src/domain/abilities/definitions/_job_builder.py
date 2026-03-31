from domain.abilities.factory import make_ability

# Core Builder

def build_job(job_name: str, definitions: list):
    """
    Registers all abilities for a job using a compact definition format.
    """

    def level(c):
        return c.get_adventure_level_by_name(job_name, 0)

    for ability_def in definitions:

        name = ability_def["name"]
        kind = ability_def.get("type", "active")  # active | passive | skill

        # Unlock condition
        unlock_condition = ability_def.get(
            "unlock",
            lambda c, lvl=ability_def.get("level", 1): (
                c.has_adventure_job(job_name)
                and level(c) >= lvl
            )
        )

        # PASSIVE
        if kind == "passive":

            def make_effect_generator(fn):
                def effect_generator(character):
                    result = fn(character)

                    # 🔥 Enforce flat List[Effect]
                    if callable(result):
                        result = result(character)

                    if not isinstance(result, list):
                        result = [result]

                    return result

                return effect_generator

            make_ability(
                name=name,
                unlock_condition=unlock_condition,
                effect_generator=make_effect_generator(ability_def["effects"]),
                duration=ability_def.get("duration", "Passive Constant"),
                description=ability_def.get("description", ""),
                is_passive=True,
                is_skill=False,
                target_type=ability_def.get("target", "self"),
            )

        # ACTIVE / SKILL
        else:

            def make_execute(fn):
                def execute(caster, targets):
                    result = fn(caster, targets)

                    # Enforce flat List[Effect] to block lazy eval issues
                    if callable(result):
                        result = result(caster)

                    if not isinstance(result, list):
                        result = [result]

                    return result

                return execute

            make_ability(
                name=name,
                unlock_condition=unlock_condition,
                execute=make_execute(ability_def["effects"]),
                cost=ability_def.get("cost", 0),
                cost_pool=ability_def.get("cost_pool"),
                duration=ability_def.get("duration"),
                description=ability_def.get("description", ""),
                is_passive=False,
                is_skill=(kind == "skill"),
                target_type=ability_def.get("target", "self"),
            )