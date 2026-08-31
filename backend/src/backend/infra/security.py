from typing import Annotated

from fastapi import Depends, Request

from backend.error import UnauthorizedError


async def get_current_user_id(request: Request) -> str:
    """Extrai o ID do usuário autenticado validado pelo middleware HMAC."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        user_id = request.headers.get("x-user-id")
    if not user_id:
        raise UnauthorizedError(message="Usuário não autenticado")
    return str(user_id)


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
