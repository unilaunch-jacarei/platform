from backend.domains.gamification.models import AchievementCode, WorkType
from backend.domains.gamification.rules import (
    ACHIEVEMENTS,
    SECONDS_PER_HOUR,
    get_level_from_seconds,
)


def test_levels_are_formed_only_by_total_hours():
    assert get_level_from_seconds(0) == 1
    assert get_level_from_seconds(10 * SECONDS_PER_HOUR) == 2
    assert get_level_from_seconds(20 * SECONDS_PER_HOUR) == 3
    assert get_level_from_seconds(30 * SECONDS_PER_HOUR) == 4
    assert get_level_from_seconds(40 * SECONDS_PER_HOUR) == 5
    assert get_level_from_seconds(100 * SECONDS_PER_HOUR) == 5


def test_fixed_work_types_and_achievements_are_defined():
    assert [item.value for item in WorkType] == [
        "back",
        "front",
        "fullstack",
        "banco_de_dados",
        "api",
    ]
    assert [item.code for item in ACHIEVEMENTS] == list(AchievementCode)
    assert [item.required_level for item in ACHIEVEMENTS] == [1, 2, 3, 4, 5]
