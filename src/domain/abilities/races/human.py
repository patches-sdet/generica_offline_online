from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  passive_modifier

build_job("Human", [
    {
    "name": "Human Flexibility",
    "type": "passive",
    "description": "Humans do not suffer a multijob penalty when receiving level points.",
    "effects": lambda ctx, targets: [
        passive_modifier(
            lambda ctx: ctx.modify_level_point_cost(multijob_penalty=0))
        ],
    },

    {
        "name": "Man's Drive to Achieve",
        "type": "passive",
        "description": "Whenever you slay a boss-level monster or complete a legendary quest, you gain an extra level point.",
        "effects": lambda ctx, targets: [
            passive_modifier(
                lambda ctx: ctx.on_event(
                    "defeat_boss",
                    lambda event_ctx: event_ctx.source.gain_level_points(1)
                )
            ),
        ],
    }
])