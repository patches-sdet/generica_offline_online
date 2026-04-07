from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ConditionalEffect(Effect):
    effect: Effect
    condition: Callable

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if self.condition(context, target):
                self.effect.apply(context.with_targets([target]))

@dataclass(slots=True)
class CompositeEffect(Effect):
    effects: list[Effect]

    def apply(self, context: EffectContext) -> None:
        for effect in self.effects:
            if effect is None:
                continue
            effect.apply(context)

@dataclass(slots=True)
class HighestWeaponSkillBonus(Effect):
    scale_fn: Callable

    def apply(self, context: EffectContext) -> None:
        character = context.source
        amount = int(self.scale_fn(character))

        weapon_skills = {
            name: level
            for name, level in character.skills.items()
            if is_weapon_skill(name)
        }

        if not weapon_skills:
            return

        highest = max(weapon_skills.values())
        tied = [name for name, level in weapon_skills.items() if level == highest]

        chosen = tied[0]  # temporary default
        character.skills[chosen] = character.skills.get(chosen, 0) + amount