from backend.domains.gamification.models import WorkType

WORK_TYPES = tuple(WorkType)


def is_work_type(value: str) -> bool:
    return value in WORK_TYPES
