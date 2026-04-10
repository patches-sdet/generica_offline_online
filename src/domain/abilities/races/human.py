from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  on_event, passive_modifier
from domain.effects.conditional import CompositeEffect
from domain.effects.special.event import GainLevelPointsEffect

build_job("Human", [
    {
    "name": "Human Flexibility",
    "required_level": 1,
    "type": "passive",
    "description": "Humans do not suffer a multijob penalty when receiving level points.",
    "effects": passive_modifier(
            lambda ctx: ctx.modify_level_point_award(multijob_penalty=-1)
            ),
    },

    {
        "name": "Man's Drive to Achieve",
        "required_level": 1,
        "type": "passive",
        "description": "Whenever you slay a boss-level monster or complete a legendary quest, you gain an extra level point.",
        "effects": CompositeEffect(
            on_event(
                "defeat_boss",
                GainLevelPointsEffect(1),
            ),
            on_event(
                "complete_legendary_quest",
                GainLevelPointsEffect(1),
            )
        ),
    }
],
source_type="race",
)