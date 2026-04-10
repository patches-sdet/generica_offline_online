from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_derived_buff
from domain.conditions import IS_ALLY

# Narrative Unlock conditions: 
# requires Knight 10, Animator 10, Tinker 10. The rest is narrative and can be adjusted as needed.
# Abilities include "Talk to the Hand" (Either negates critical hits, reduces damage, or increases armor) and "Steam Scream" which does moxie damage to all enemies in earshot

build_job("Steam-Knight", [],
source_type="advanced"
)

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
