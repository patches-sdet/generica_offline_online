from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff
from domain.conditions import IS_ALLY

build_job("Oracle", [

    # Lesser Healing
    {"grant": "Lesser Healing", "required_level": 1},

])
