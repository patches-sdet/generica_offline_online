from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING, List
from domain.effects import Effect, StatIncrease

if TYPE_CHECKING:
    from domain.character import Character

@dataclass(frozen=True)
class Ability:
    name: str
    unlock_condition: Callable[["Character"], bool]
    effects: list[Effect] = field(default_factory = list)

    effect_generator: Callable[["Character"], List[Effect]] | None = None

    def get_effects(self, character: "Character") -> List[Effect]:
        if self.effect_generator:
            return self.effect_generator(character)
        return self.effects

ALL_ABILITIES = []

def register_ability(ability):
    ALL_ABILITIES.append(ability)

def make_ability(name:str, unlock_condition, effects=None, effect_generator=None):
    ability = Ability(
            name = name,
            unlock_condition = unlock_condition,
            effects = effects or [],
            effect_generator = effect_generator,
            )
    register_ability(ability)
    return ability

# Adventure Job abilities

# Alchemist Job

make_ability(
    "Analyze",
    unlock_condition = lambda c: (
        c.adventure_job
        and c.adventure_job.name == "Alchemist"
        and c.adventure_level >= 1
    )
)

make_ability(
    "Bomb",
    unlock_condition = lambda c: (
        c.adventure_job
        and c.adventure_job.name == "Alchemist"
        and c.adventure_level >= 1
    )
)

# Distill
# Healing Potion
# Mana Potion

# Animator Job

# Animus
# Command Animus

def creators_guardians_effect(character):
    level = character.ability_levels.get("Creator's Guardians", 1)
    will = character.attributes.willpower

    bonus = (will + level) // 10

    effects = []

    for attr_name, value in vars(character.attributes).items():
        if value > 0:
            effects.append(StatIncrease(attr_name, bonus))
        return effects

make_ability(
    "Creator's Guardians",
    unlock_condition = lambda c: (
        c.adventure_job
        and c.adventure_job.name == "Animator"
        and c.adventure_level >= 1
    ),
    effect_generator=creators_guardians_effect
)

make_ability(
    "Eye for Detail",
    unlock_condition = lambda c: (
        c.adventure_job
        and c.adventure_job.name == "Animator"
        and c.adventure_level >= 1
    )
)

make_ability(
    "Mend",
    unlock_condition = lambda c: (
        c.adventure_job
        and c.adventure_job.name == "Animator"
        and c.adventure_level >= 1
    )
)

# Archer Job

make_ability(
    "Aim",
    unlock_condition = lambda c: (
        c.adventure_job
        and c.adventure_job.name == "Archer"
        and c.adventure_level >= 1
    )
)
