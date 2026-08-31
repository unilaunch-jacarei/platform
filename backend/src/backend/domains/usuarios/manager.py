import logging
import uuid
from typing import AsyncGenerator

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from backend.config import Settings, get_settings
from backend.domains.usuarios.db import get_user_db
from backend.domains.usuarios.models import User

logger = logging.getLogger("backend.auth")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    def __init__(self, user_db, settings: Settings):
        super().__init__(user_db)
        self.reset_password_token_secret = settings.jwt_secret
        self.verification_token_secret = settings.jwt_secret

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.info("Usuário registrado com sucesso: %s (%s)", user.id, user.email)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.info("Solicitação de recuperação de senha para: %s (token=%s)", user.email, token)

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None):
        logger.info("Solicitação de verificação de e-mail para: %s", user.email)


async def get_user_manager(
    user_db=Depends(get_user_db),
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db, settings)
