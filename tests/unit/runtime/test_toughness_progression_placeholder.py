"""Starter placeholder for Toughness runtime rank-up tests.

Target behavior:
- single-hit damage > constitution + Toughness rank
- Toughness gains a rank
- recalculate() updates max_hp by +2 per rank
"""

import pytest


@pytest.mark.skip(reason="Toughness rank-up belongs in runtime/event handling and should be tested once that API stabilizes.")
def test_toughness_rank_up_placeholder():
    assert True
