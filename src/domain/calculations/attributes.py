from domain.character import Character
from domain.effects import EffectContext
from domain.attributes import Attributes
from domain.effects.stat_effects import StatIncrease, MultiStatIncrease


ATTRIBUTE_EFFECT_TYPES = (StatIncrease, MultiStatIncrease)


def rebuild_attributes(character: Character, effects: list) -> None:
    """
    Rebuild only base/additive attributes from aggregated effects.
    """

    character.attributes = Attributes()
    character._attribute_sources.clear()

    context = EffectContext(
        source="rebuild_attributes",
        targets=[character],
    )

    for effect in effects:
        if isinstance(effect, ATTRIBUTE_EFFECT_TYPES):
            effect.apply(context)

    character._base_attributes = character.attributes.to_dict()