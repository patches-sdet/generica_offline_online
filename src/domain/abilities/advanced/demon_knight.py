from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff
from domain.conditions import IS_ALLY

# Narrative Unlock conditions: 
# requires Cultist 25, Knight 25. The rest is narrative and can be adjusted as needed.

build_job("Demon-Knight", [])

#     # -------------------------
#     # Passive
#     # -------------------------
#     {
#         "name": "Faith",
#         "type": "passive",
#         "effects": lambda c: scaled_derived_buff(
#             stat="fate",
#             scale_fn=lambda c: c.get_adventure_level_by_name("Demon-Knight", 0),
#         )(c),
#         "description": "Your Fate increases with Demon-Knight level.",
#     },

#     # -------------------------
#     # Example Skill
#     # -------------------------
#     {
#         "name": "Example Skill",
#         "type": "skill",
#         "cost": 1,
#         "cost_pool": "fortune",
#         "target": "ally",
#         "effects": lambda caster, targets: [
#             buff(
#                 scale_fn=lambda c: c.pools.get("fortune", 0),
#                 stats={"any": 1},
#                 condition=IS_ALLY,
#             )
#         ],
#     },

# ])
