from __future__ import annotations

from helpers.builders import make_recalculated_character


def bear_berserker():
    return make_recalculated_character(
        name="Bear Berserker",
        progressions=[
            ("race", "Bear", 1),
            ("adventure", "Berserker", 1),
        ],
    )


def cleric_oracle():
    return make_recalculated_character(
        name="Cleric Oracle",
        progressions=[
            ("adventure", "Cleric", 1),
            ("adventure", "Oracle", 1),
        ],
    )
