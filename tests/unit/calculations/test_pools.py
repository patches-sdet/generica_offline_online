from domain.attributes import Attributes
from domain.calculations.pools import calculate_pools


class _CharacterStub:
    def __init__(self, *, toughness_rank: int = 0):
        self.attributes = Attributes()
        self.ability_levels = {}
        if toughness_rank:
            self.ability_levels["Toughness"] = toughness_rank

        self.current_hp = 0
        self.current_sanity = 0
        self.current_stamina = 0
        self.current_moxie = 0
        self.current_fortune = 0

        self.max_hp = 0
        self.max_sanity = 0
        self.max_stamina = 0
        self.max_moxie = 0
        self.max_fortune = 0


def test_calculate_pools_without_toughness_uses_base_formulas():
    character = _CharacterStub()

    pools = calculate_pools(character)

    assert character.max_hp == 50
    assert character.max_sanity == 50
    assert character.max_stamina == 50
    assert character.max_moxie == 50
    assert character.max_fortune == 50

    assert pools.hp == (0, 50)
    assert pools.sanity == (0, 50)
    assert pools.stamina == (0, 50)
    assert pools.moxie == (0, 50)
    assert pools.fortune == (0, 50)


def test_calculate_pools_with_toughness_adds_hp_only():
    character = _CharacterStub(toughness_rank=3)

    pools = calculate_pools(character)

    assert character.max_hp == 56
    assert character.max_sanity == 50
    assert character.max_stamina == 50
    assert character.max_moxie == 50
    assert character.max_fortune == 50

    assert pools.hp == (0, 56)
    assert pools.sanity == (0, 50)
    assert pools.stamina == (0, 50)
    assert pools.moxie == (0, 50)
    assert pools.fortune == (0, 50)


def test_calculate_pools_clamps_current_values_to_new_maxima():
    character = _CharacterStub(toughness_rank=2)
    character.current_hp = 999
    character.current_sanity = 999
    character.current_stamina = 999
    character.current_moxie = 999
    character.current_fortune = 999

    pools = calculate_pools(character)

    assert character.max_hp == 54
    assert character.max_sanity == 50
    assert character.max_stamina == 50
    assert character.max_moxie == 50
    assert character.max_fortune == 50

    assert character.current_hp == 54
    assert character.current_sanity == 50
    assert character.current_stamina == 50
    assert character.current_moxie == 50
    assert character.current_fortune == 50

    assert pools.hp == (54, 54)
    assert pools.sanity == (50, 50)
    assert pools.stamina == (50, 50)
    assert pools.moxie == (50, 50)
    assert pools.fortune == (50, 50)