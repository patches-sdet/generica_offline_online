class Effect:
    def apply(self, character):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()

class StatIncrease(Effect):
    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, character):
        current = getattr(character.attributes, self.stat)
        setattr(character.attributes, self.stat, current + self.amount)

    def to_dict(self):
        return {
                "type": "stat_increase",
                "stat": self.stat,
                "amount": self.amount,
                }

def make_effects(**mods):
    return [StatIncrease(stat, value) for stat, value in mods.items()]
