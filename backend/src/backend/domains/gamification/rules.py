from dataclasses import dataclass

from backend.domains.gamification.models import AchievementCode

SECONDS_PER_HOUR = 60 * 60
LEVEL_HOURS = {
    1: 0,
    2: 10,
    3: 20,
    4: 30,
    5: 40,
}


@dataclass(frozen=True)
class AchievementDefinition:
    code: AchievementCode
    name: str
    description: str
    required_level: int


ACHIEVEMENTS = (
    AchievementDefinition(AchievementCode.INITIAL, "Inicial", "Alcance o nível Inicial.", 1),
    AchievementDefinition(AchievementCode.BASIC, "Básico", "Alcance o nível Básico.", 2),
    AchievementDefinition(AchievementCode.MEDIUM, "Mediano", "Alcance o nível Mediano.", 3),
    AchievementDefinition(AchievementCode.ADVANCED, "Avançado", "Alcance o nível Avançado.", 4),
    AchievementDefinition(AchievementCode.MASTER, "Mestre", "Alcance o nível Mestre.", 5),
)


def get_level_from_seconds(total_seconds: int) -> int:
    level = 1
    for candidate, required_hours in LEVEL_HOURS.items():
        if total_seconds >= required_hours * SECONDS_PER_HOUR:
            level = candidate
    return level


def get_level_name(level: int) -> str:
    return next(
        achievement.name for achievement in ACHIEVEMENTS if achievement.required_level == level
    )
