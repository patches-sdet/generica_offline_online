from dataclasses import dataclass, field
from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease

@dataclass(frozen=True, slots=True)
class ProfessionJob:
    name: str
    effects_on_acquire: tuple[Effect, ...] = field(default_factory=tuple)
    effects_per_level: tuple[Effect, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)

    def get_effects(self, level: int) -> list[Effect]:
        level = max(1, level)
        return list(self.effects_per_level) * max(0, level - 1)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "effects_on_acquire": [str(e) for e in self.effects_on_acquire],
            "effects_per_level": [str(e) for e in self.effects_per_level],
            "tags": list(self.tags),
        }


def make_effects(**mods) -> tuple[Effect, ...]:
    return tuple(StatIncrease(stat, value) for stat, value in mods.items())


PROFESSION_JOB_DEFINITIONS: tuple[ProfessionJob, ...] = (
    ProfessionJob(
        name="Brewer",
        effects_on_acquire=make_effects(constitution=1, perception=1),
        effects_per_level=make_effects(constitution=1, perception=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Carpenter",
        effects_on_acquire=make_effects(strength=1, dexterity=1),
        effects_per_level=make_effects(strength=1, dexterity=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Cook",
        effects_on_acquire=make_effects(perception=1, luck=1),
        effects_per_level=make_effects(perception=1, luck=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Jeweler",
        effects_on_acquire=make_effects(wisdom=1, luck=1),
        effects_per_level=make_effects(wisdom=1, luck=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Mason",
        effects_on_acquire=make_effects(strength=1, constitution=1),
        effects_per_level=make_effects(strength=1, constitution=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Midwife",
        effects_on_acquire=make_effects(constitution=1, luck=1),
        effects_per_level=make_effects(constitution=1, luck=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Miner",
        effects_on_acquire=make_effects(strength=1, dexterity=1),
        effects_per_level=make_effects(strength=1, dexterity=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Sculptor",
        effects_on_acquire=make_effects(dexterity=1, perception=1),
        effects_per_level=make_effects(dexterity=1, perception=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Smith",
        effects_on_acquire=make_effects(strength=1, constitution=1),
        effects_per_level=make_effects(strength=1, constitution=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Tailor",
        effects_on_acquire=make_effects(dexterity=1, perception=1),
        effects_per_level=make_effects(dexterity=1, perception=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Tanner",
        effects_on_acquire=make_effects(dexterity=1, agility=1),
        effects_per_level=make_effects(dexterity=1, agility=1),
        tags=("utility",),
    ),
    ProfessionJob(
        name="Tinker",
        effects_on_acquire=make_effects(dexterity=1, intelligence=1),
        effects_per_level=make_effects(dexterity=1, intelligence=1),
        tags=("utility",),
    ),
)