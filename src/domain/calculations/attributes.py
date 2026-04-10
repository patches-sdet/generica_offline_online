from domain.character import Character
from domain.effects import EffectContext
from domain.attributes import Attributes, DEFAULT_STATS
from domain.effects.stat_effects import StatIncrease, MultiStatIncrease


ATTRIBUTE_EFFECT_TYPES = (StatIncrease, MultiStatIncrease)


def rebuild_attributes(character: Character, effects: list) -> None:
    """
    Rebuild only base/additive attributes from aggregated effects.
    """
    character.attributes = Attributes()
    character._attribute_sources.clear()

    base_attributes = character._base_attributes or dict(DEFAULT_STATS)

    for stat, value in base_attributes.items():
        character.set_stat(stat, value)
        character._attribute_sources[stat]["Base"] += value

    context = EffectContext(
        source=character,
        targets=[character],
    )

    for effect in effects:
        if isinstance(effect, ATTRIBUTE_EFFECT_TYPES):
            effect.apply(context)
