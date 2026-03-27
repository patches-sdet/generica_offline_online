from domain.attributes import STAT_FORMULAS, Pools


def calculate_pools(character):
    a = character.attributes

    values = {
        key: STAT_FORMULAS[key](a)
        for key in STAT_FORMULAS
    }

    return Pools(
        hp=(character.current_hp, values["hp"]),
        sanity=(character.current_sanity, values["sanity"]),
        stamina=(character.current_stamina, values["stamina"]),
        moxie=(character.current_moxie, values["moxie"]),
        fortune=(character.current_fortune, values["fortune"]),
    )
