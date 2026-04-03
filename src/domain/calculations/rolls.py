@dataclass(slots=True)
class RollContext:
    actor: Any
    target: Any | None = None
    roll_type: str = ""
    tags: set[str] = field(default_factory=set)

def get_total_roll_modifiers(character):
    return sum(mod.value for mod in character.roll_modifiers)

def apply_roll_modifiers(character, base_roll):
    total_modifiers = get_total_roll_modifiers(character)
    return base_roll + total_modifiers