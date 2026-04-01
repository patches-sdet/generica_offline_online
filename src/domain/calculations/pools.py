from domain.attributes import STAT_FORMULAS, Pools


def calculate_pools(character) -> Pools:
    """
    Recalculate poolsfrom rebuilt attributes.
    Does not modify current resource values unless they exceed new max.
    """

    a = character.attributes

    values = {
        key: STAT_FORMULAS[key](a)
        for key in STAT_FORMULAS
    }

    # Store max
    character.max_hp = values["hp"]
    character.max_sanity = values["sanity"]
    character.max_stamina = values["stamina"]
    character.max_moxie = values["moxie"]
    character.max_fortune = values["fortune"]

    # Clamp current values if necessary
    character.current_hp = min(character.current_hp, character.max_hp)
    character.current_sanity = min(character.current_sanity, character.max_sanity)
    character.current_stamina = min(character.current_stamina, character.max_stamina)
    character.current_moxie = min(character.current_moxie, character.max_moxie)
    character.current_fortune = min(character.current_fortune, character.max_fortune)

    pools = Pools(
        hp=(character.current_hp, character.max_hp),
        sanity=(character.current_sanity, character.max_sanity),
        stamina=(character.current_stamina, character.max_stamina),
        moxie=(character.current_moxie, character.max_moxie),
        fortune=(character.current_fortune, character.max_fortune),
    )

    character.pools = pools

    return pools