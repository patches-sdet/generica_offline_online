from dataclasses import dataclass, field

from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease


@dataclass(frozen=True, slots=True)
class AdvancedJob:
    name: str
    effects_on_acquire: tuple[Effect, ...] = field(default_factory=tuple)
    effects_per_level: tuple[Effect, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)

    def get_effects(self, level: int) -> list[Effect]:
        level = max(1, level)

        effects = list(self.effects_on_acquire)

        if level > 1:
            effects.extend(self.effects_per_level * (level - 1))

        return effects

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "effects_on_acquire": [str(e) for e in self.effects_on_acquire],
            "effects_per_level": [str(e) for e in self.effects_per_level],
            "tags": list(self.tags),
        }

def make_effects(source: str | None = None, **mods) -> tuple[Effect, ...]:
    return tuple(StatIncrease(stat, value, source=source) for stat, value in mods.items())

ADVANCED_JOB_DEFINITIONS: tuple[AdvancedJob, ...] = (
    AdvancedJob(
        name="Bounty Hunter",
        effects_on_acquire=make_effects(source="Bounty Hunter", dexterity=5, perception=5),
        effects_per_level=make_effects(source="Bounty Hunter", dexterity=5, perception=5),
        tags=("precision", "utility"),
    ),
    AdvancedJob(
        name="Courtier",
        effects_on_acquire=make_effects(source="Courtier", charisma=5, wisdom=5),
        effects_per_level=make_effects(source="Courtier", charisma=5, wisdom=5),
        tags=("social", "support"),
    ),
    AdvancedJob(
        name="Death Knight",
        effects_on_acquire=make_effects(source="Death Knight", intelligence=5, constitution=5),
        effects_per_level=make_effects(source="Death Knight", intelligence=5, constitution=5),
        tags=("minion", "plague"),
    ),
    AdvancedJob(
        name="Demon Knight",
        effects_on_acquire=make_effects(source="Demon Knight", strength=5, willpower=5),
        effects_per_level=make_effects(source="Demon Knight", strength=5, willpower=5),
        tags=("melee", "aggressive"),
    ),
    AdvancedJob(
        name="Detective",
        effects_on_acquire=make_effects(source="Detective", intelligence=5, perception=5),
        effects_per_level=make_effects(source="Detective", intelligence=5, perception=5),
        tags=("utility", "precision"),
    ),
    AdvancedJob(
        name="Doomsayer",
        effects_on_acquire=make_effects(source="Doomsayer", wisdom=5, willpower=5),
        effects_per_level=make_effects(source="Doomsayer", wisdom=5, willpower=5),
        tags=("support", "aggressive"),
    ),
    AdvancedJob(
        name="Gambler",
        effects_on_acquire=make_effects(source="Gambler", charisma=5, luck=5),
        effects_per_level=make_effects(source="Gambler", charisma=5, luck=5),
        tags=("utility", "social"),
    ),
    AdvancedJob(
        name="Godbinder",
        effects_on_acquire=make_effects(source="Godbinder", willpower=5, luck=5),
        effects_per_level=make_effects(source="Godbinder", willpower=5, luck=5),
        tags=("support", "caster"),
    ),
    AdvancedJob(
        name="Golemist",
        effects_on_acquire=make_effects(source="Golemist", intelligence=5, willpower=5),
        effects_per_level=make_effects(source="Golemist", intelligence=5, willpower=5),
        tags=("support", "buff", "creation"),
    ),
    AdvancedJob(
        name="Guild Master",
        effects_on_acquire=make_effects(source="Guild Master", charisma=5, intelligence=5),
        effects_per_level=make_effects(source="Guild Master", charisma=5, intelligence=5),
        tags=("support", "social", "utility"),
    ),
    AdvancedJob(
        name="Lich",
        effects_on_acquire=make_effects(source="Lich", intelligence=5, willpower=5),
        effects_per_level=make_effects(source="Lich", intelligence=5, willpower=5),
        tags=("caster", "control"),
    ),
    AdvancedJob(
        name="Paladin",
        effects_on_acquire=make_effects(source="Paladin", constitution=5, wisdom=5),
        effects_per_level=make_effects(source="Paladin", constitution=5, wisdom=5),
        tags=("defensive", "support"),
    ),
    AdvancedJob(
        name="Pirate",
        effects_on_acquire=make_effects(source="Pirate", dexterity=5, agility=5),
        effects_per_level=make_effects(source="Pirate", dexterity=5, agility=5),
        tags=("aggressive", "utility"),
    ),
    AdvancedJob(
        name="Ranger",
        effects_on_acquire=make_effects(source="Ranger", perception=5, wisdom=5),
        effects_per_level=make_effects(source="Ranger", perception=5, wisdom=5),
        tags=("ranged", "utility"),
    ),
    AdvancedJob(
        name="Steam Knight",
        effects_on_acquire=make_effects(source="Steam Knight", strength=5, intelligence=5),
        effects_per_level=make_effects(source="Steam Knight", strength=5, intelligence=5),
        tags=("defensive", "creation"),
    ),
)