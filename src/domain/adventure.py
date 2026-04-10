from dataclasses import dataclass, field
from domain.effects.base import Effect
from domain.effects.stat_effects import StatIncrease


CLASS_REGISTRY = {
    "S": "Sage",
    "C": "Creator",
    "W": "Warrior",
    "R": "Rogue",
    "D": "Diva",
    "P": "Priest",
    "E": "Wanderer",
}

JOB_CLASS_MAP = {
    "Alchemist": "S",
    "Animator": "C",
    "Archer": "W",
    "Assassin": "R",
    "Bandit": "R",
    "Bard": "D",
    "Berserker": "W",
    "Burglar": "R",
    "Cleric": "P",
    "Conjuror": "C",
    "Cultist": "P",
    "Duelist": "W",
    "Elementalist": "C",
    "Enchanter": "S",
    "Explorer": "E",
    "Grifter": "R",
    "Knight": "W",
    "Mercenary": "E",
    "Merchant": "E",
    "Model": "D",
    "Necromancer": "C",
    "Oracle": "P",
    "Ruler": "D",
    "Scout": "E",
    "Sensate": "D",
    "Shaman": "P",
    "Tamer": "S",
    "Wizard": "S",
}


@dataclass(frozen=True, slots=True)
class AdventureJob:
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

    @property
    def class_code(self) -> str:
        return JOB_CLASS_MAP[self.name]

    @property
    def job_class(self) -> str:
        return CLASS_REGISTRY[self.class_code]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "effects_on_acquire": [str(e) for e in self.effects_on_acquire],
            "effects_per_level": [str(e) for e in self.effects_per_level],
            "tags": list(self.tags),
        }


def make_effects(source: str | None =  None, **mods) -> tuple[Effect, ...]:
    return tuple(StatIncrease(stat, value, source=source) for stat, value in mods.items())


ADVENTURE_JOB_DEFINITIONS: tuple[AdventureJob, ...] = (
    AdventureJob(
        name="Animator",
        effects_on_acquire=make_effects(source="Animator", dexterity=3, intelligence=3, willpower=3),
        effects_per_level=make_effects(source="Animator", dexterity=3, intelligence=3, willpower=3),
        tags=("creation", "minions", "support"),
    ),
    AdventureJob(
        name="Conjuror",
        effects_on_acquire=make_effects(source="Conjuror", charisma=3, intelligence=3, willpower=3),
        effects_per_level=make_effects(source="Conjuror", charisma=3, intelligence=3, willpower=3),
        tags=("creation", "minions", "support"),
    ),
    AdventureJob(
        name="Elementalist",
        effects_on_acquire=make_effects(source="Elementalist", constitution=3, intelligence=3, willpower=3),
        effects_per_level=make_effects(source="Elementalist", constitution=3, intelligence=3, willpower=3),
        tags=("damage", "minions", "support"),
    ),
    AdventureJob(
        name="Necromancer",
        effects_on_acquire=make_effects(source="Necromancer", intelligence=3, willpower=3, wisdom=3),
        effects_per_level=make_effects(source="Necromancer", intelligence=3, willpower=3, wisdom=3),
        tags=("creation", "minions", "support"),
    ),
    AdventureJob(
        name="Bard",
        effects_on_acquire=make_effects(source="Bard", charisma=3, dexterity=3, luck=3),
        effects_per_level=make_effects(source="Bard", charisma=3, dexterity=3, luck=3),
        tags=("support", "buffs", "debuff"),
    ),
    AdventureJob(
        name="Model",
        effects_on_acquire=make_effects(source="Model", agility=3, charisma=3, perception=3),
        effects_per_level=make_effects(source="Model", agility=3, charisma=3, perception=3),
        tags=("buffs", "social"),
    ),
    AdventureJob(
        name="Ruler",
        effects_on_acquire=make_effects(source="Ruler", charisma=3, wisdom=3, luck=3),
        effects_per_level=make_effects(source="Ruler", charisma=3, wisdom=3, luck=3),
        tags=("buffs", "social", "control"),
    ),
    AdventureJob(
        name="Sensate",
        effects_on_acquire=make_effects(source="Sensate", charisma=3, intelligence=3, perception=3),
        effects_per_level=make_effects(source="Sensate", charisma=3, intelligence=3, perception=3),
        tags=("defensive", "illusion", "support"),
    ),
    AdventureJob(
        name="Explorer",
        effects_on_acquire=make_effects(source="Explorer", constitution=3, intelligence=3, willpower=3),
        effects_per_level=make_effects(source="Explorer", constitution=3, intelligence=3, willpower=3),
        tags=("movement","ranged", "utility"),
    ),
    AdventureJob(
        name="Merchant",
        effects_on_acquire=make_effects(source="Merchant", charisma=3, intelligence=3, perception=3),
        effects_per_level=make_effects(source="Merchant", charisma=3, intelligence=3, perception=3),
        tags=("utility",),
    ),
    AdventureJob(
        name="Mercenary",
        effects_on_acquire=make_effects(source="Mercenary", dexterity=3, perception=3, strength=3),
        effects_per_level=make_effects(source="Mercenary", dexterity=3, perception=3, strength=3),
        tags=("melee", "utility", "buffs"),
    ),
    AdventureJob(
        name="Scout",
        effects_on_acquire=make_effects(source="Scout", agility=3, perception=3, wisdom=3),
        effects_per_level=make_effects(source="Scout", agility=3, perception=3, wisdom=3),
        tags=("stealth", "utility"),
    ),
    AdventureJob(
        name="Cleric",
        effects_on_acquire=make_effects(source="Cleric", constitution=3, luck=3, wisdom=3),
        effects_per_level=make_effects(source="Cleric", constitution=3, luck=3, wisdom=3),
        tags=("support", "healer", "buffs"),
    ),
    AdventureJob(
        name="Cultist",
        effects_on_acquire=make_effects(source="Cultist", charisma=3, intelligence=3, luck=3),
        effects_per_level=make_effects(source="Cultist", charisma=3, intelligence=3, luck=3),
        tags=("aggressive", "curse", "debuff"),
    ),
    AdventureJob(
        name="Oracle",
        effects_on_acquire=make_effects(source="Oracle", charisma=3, luck=3, wisdom=3),
        effects_per_level=make_effects(source="Oracle", charisma=3, luck=3, wisdom=3),
        tags=("support", "healer", "buffs"),
    ),
    AdventureJob(
        name="Shaman",
        effects_on_acquire=make_effects(source="Shaman", luck=3, strength=3, wisdom=3),
        effects_per_level=make_effects(source="Shaman", luck=3, strength=3, wisdom=3),
        tags=("aggressive", "healer", "buffs"),
    ),
    AdventureJob(
        name="Assassin",
        effects_on_acquire=make_effects(source="Assassin", agility=3, charisma=3, dexterity=3),
        effects_per_level=make_effects(source="Assassin", agility=3, charisma=3, dexterity=3),
        tags=("precision", "stealth", "movement"),
    ),
    AdventureJob(
        name="Bandit",
        effects_on_acquire=make_effects(source="Bandit", agility=3, strength=3, wisdom=3),
        effects_per_level=make_effects(source="Bandit", agility=3, strength=3, wisdom=3),
        tags=("aggressive", "minions", "utility"),
    ),
    AdventureJob(
        name="Burglar",
        effects_on_acquire=make_effects(source="Burglar", dexterity=3, perception=3, agility=3),
        effects_per_level=make_effects(source="Burglar", dexterity=3, perception=3, agility=3),
        tags=("stealth", "movement", "utility"),
    ),
    AdventureJob(
        name="Grifter",
        effects_on_acquire=make_effects(source="Grifter", charisma=3, dexterity=3, luck=3),
        effects_per_level=make_effects(source="Grifter", charisma=3, dexterity=3, luck=3),
        tags=("social", "utility", "debuff"),
    ),
    AdventureJob(
        name="Alchemist",
        effects_on_acquire=make_effects(source="Alchemist", constitution=3, intelligence=3, dexterity=3),
        effects_per_level=make_effects(source="Alchemist", constitution=3, intelligence=3, dexterity=3),
        tags=("aggressive", "crafting", "utility"),
    ),
    AdventureJob(
        name="Enchanter",
        effects_on_acquire=make_effects(source="Enchanter", dexterity=3, intelligence=3, willpower=3),
        effects_per_level=make_effects(source="Enchanter", dexterity=3, intelligence=3, willpower=3),
        tags=("buffs", "crafting", "utility"),
    ),
    AdventureJob(
        name="Tamer",
        effects_on_acquire=make_effects(source="Tamer", charisma=3, perception=3, constitution=3),
        effects_per_level=make_effects(source="Tamer", charisma=3, perception=3, constitution=3),
        tags=("buffs", "caster", "minions"),
    ),
    AdventureJob(
        name="Wizard",
        effects_on_acquire=make_effects(source="Wizard", intelligence=3, willpower=3, wisdom=3),
        effects_per_level=make_effects(source="Wizard", intelligence=3, willpower=3, wisdom=3),
        tags=("aggressive", "caster", "powerful"),
    ),
    AdventureJob(
        name="Archer",
        effects_on_acquire=make_effects(source="Archer", dexterity=3, perception=3, strength=3),
        effects_per_level=make_effects(source="Archer", dexterity=3, perception=3, strength=3),
        tags=("precision", "ranged", "utility"),
    ),
    AdventureJob(
        name="Berserker",
        effects_on_acquire=make_effects(source="Berserker", constitution=3, strength=3, willpower=3),
        effects_per_level=make_effects(source="Berserker", constitution=3, strength=3, willpower=3),
        tags=("aggressive", "melee", "movement"),
    ),
    AdventureJob(
        name="Duelist",
        effects_on_acquire=make_effects(source="Duelist", agility=3, dexterity=3, strength=3),
        effects_per_level=make_effects(source="Duelist", agility=3, dexterity=3, strength=3),
        tags=("defensive", "melee", "precision"),
    ),
    AdventureJob(
        name="Knight",
        effects_on_acquire=make_effects(source="Knight", charisma=3, constitution=3, strength=3),
        effects_per_level=make_effects(source="Knight", charisma=3, constitution=3, strength=3),
        tags=("control", "melee", "mounted"),
    ),
)