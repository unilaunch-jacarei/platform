from backend.domains.boards.dependencies import get_user_board_role, require_board_role
from backend.domains.boards.manager import BoardManager, board_manager
from backend.domains.boards.models import Board, BoardMember, BoardRole
from backend.domains.boards.routes import boards_router
from backend.domains.boards.schemas import (
    BoardCreate,
    BoardMemberCreate,
    BoardMemberRead,
    BoardMemberUpdate,
    BoardMemberUserRead,
    BoardRead,
    BoardUpdate,
)

__all__ = [
    "Board",
    "BoardMember",
    "BoardRole",
    "BoardCreate",
    "BoardRead",
    "BoardUpdate",
    "BoardMemberCreate",
    "BoardMemberRead",
    "BoardMemberUpdate",
    "BoardMemberUserRead",
    "BoardManager",
    "board_manager",
    "boards_router",
    "require_board_role",
    "get_user_board_role",
]
