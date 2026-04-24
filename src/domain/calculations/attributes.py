from domain.character import Character
from domain.effects import EffectContext
from domain.attributes import Attributes, DEFAULT_STATS
from domain.effects.stat_effects import StatIncrease, MultiStatIncrease


ATTRIBUTE_EFFECT_TYPES = (StatIncrease, MultiStatIncrease)


def rebuild_attributes(character: Character, effects: list) -> None:
    """
    Rebuild only base/additive attributes from canonical persistent inputs
    plus aggregated effects.

    Order:
      1. Creation-time base (_base_attributes or DEFAULT_STATS)
      2. Persistent manual/runtime/level-up increases
      3. Aggregated rebuild-time attribute effects
    """
    character.attributes = Attributes()
    character._attribute_sources.clear()

    base_attributes = character._base_attributes or dict(DEFAULT_STATS)

    for stat, value in base_attributes.items():
        character.set_stat(stat, value)
        character._attribute_sources[stat]["Base"] += value

    # Persistent non-progression gains that must survive rebuild.
    for stat, source_map in character.manual_attribute_increases.items():
        for source, amount in source_map.items():
            if amount != 0:
                character.add_stat(stat, amount, source=source)

    context = EffectContext(
        source=character,
        targets=[character],
    )

    for effect in effects:
        if isinstance(effect, ATTRIBUTE_EFFECT_TYPES):
            effect.apply(context)