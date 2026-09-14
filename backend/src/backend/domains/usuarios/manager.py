import logging
import uuid
from typing import AsyncGenerator

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from backend.config import Settings, get_settings
from backend.domains.usuarios.db import get_user_db
from backend.domains.usuarios.models import User
from backend.infra.email import send_password_reset_email

logger = logging.getLogger("backend.auth")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    def __init__(self, user_db, settings: Settings):
        super().__init__(user_db)
        self.reset_password_token_secret = settings.jwt_secret
        self.verification_token_secret = settings.jwt_secret
        self.settings = settings

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.info("Usuário registrado com sucesso: %s (%s)", user.id, user.email)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        sent = await send_password_reset_email(self.settings, str(user.email), token)
        if not sent:
            logger.warning("E-mail de recuperação não configurado para o usuário %s", user.id)

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None):
        logger.info("Solicitação de verificação de e-mail para: %s", user.email)


async def get_user_manager(
    user_db=Depends(get_user_db),
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db, settings)
