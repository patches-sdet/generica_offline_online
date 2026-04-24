from domain.character import Character
from application.leveling import (
    can_spend_level_points,
    award_level_points,
    spend_level_points,
    can_spend_grind_points,
    award_grind_points,
    spend_grind_points,
)


def test_award_level_points_increases_total():
    c = Character(name="Points Test")
    assert c.level_points == 0

    award_level_points(c, 3)

    assert c.level_points == 3


def test_spend_level_points_reduces_total():
    c = Character(name="Points Test")
    award_level_points(c, 5)

    spend_level_points(c, 2)

    assert c.level_points == 3


def test_can_spend_level_points_true_when_enough():
    c = Character(name="Points Test")
    award_level_points(c, 4)

    assert can_spend_level_points(c, 4) is True
    assert can_spend_level_points(c, 3) is True


def test_can_spend_level_points_false_when_not_enough():
    c = Character(name="Points Test")
    award_level_points(c, 2)

    assert can_spend_level_points(c, 3) is False


def test_spend_level_points_raises_when_not_enough():
    c = Character(name="Points Test")
    award_level_points(c, 1)

    try:
        spend_level_points(c, 2)
        assert False, "Expected ValueError for overspending level points"
    except ValueError as e:
        assert "Not enough level points" in str(e)


def test_award_level_points_rejects_non_positive_values():
    c = Character(name="Points Test")

    for bad_amount in (0, -1):
        try:
            award_level_points(c, bad_amount)
            assert False, "Expected ValueError for non-positive award"
        except ValueError:
            pass


def test_spend_level_points_rejects_non_positive_values():
    c = Character(name="Points Test")
    award_level_points(c, 3)

    for bad_amount in (0, -1):
        try:
            spend_level_points(c, bad_amount)
            assert False, "Expected ValueError for non-positive spend"
        except ValueError:
            pass


def test_award_grind_points_increases_total():
    c = Character(name="Grind Test")
    assert c.grind_points == 0

    award_grind_points(c, 4)

    assert c.grind_points == 4


def test_spend_grind_points_reduces_total():
    c = Character(name="Grind Test")
    award_grind_points(c, 6)

    spend_grind_points(c, 2)

    assert c.grind_points == 4


def test_can_spend_grind_points_false_when_not_enough():
    c = Character(name="Grind Test")
    award_grind_points(c, 1)

    assert can_spend_grind_points(c, 2) is False


def test_spend_grind_points_raises_when_not_enough():
    c = Character(name="Grind Test")
    award_grind_points(c, 1)

    try:
        spend_grind_points(c, 2)
        assert False, "Expected ValueError for overspending grind points"
    except ValueError as e:
        assert "Not enough grind points" in str(e)