from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff
from domain.conditions import IS_ALLY

# Narrative Unlock conditions: 
# requires Enchanter 10, Animator 10. The rest is narrative and can be adjusted as needed.
# Known abilities include "Animate Golem" (Infuses a golem body with life), "Mend Golem" (A heal that only targets golems, but heals for ~4x normal Mend and costs 4x the normal Mend), "Greater Golem Upgrade" (Infuses a golem with greater power, including mental attributes)

build_job("Golemist", [])
#     # -------------------------
#     # Passive
#     # -------------------------
#     {
#         "name": "Faith",
#         "type": "passive",
#         "effects": lambda c: scaled_derived_buff(
#             stat="fate",
#             scale_fn=lambda c: c.get_adventure_level_by_name("Doomsayer", 0),
#         )(c),
#         "description": "Your Fate increases with Doomsayer level.",
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
