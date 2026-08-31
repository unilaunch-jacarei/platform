from fastapi import APIRouter

from backend.domains.usuarios.auth import auth_backend, fastapi_users
from backend.domains.usuarios.schemas import UserCreate, UserRead, UserUpdate

auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/usuarios", tags=["usuarios"])

# Rotas de Autenticação JWT (/api/v1/auth/jwt/login, /api/v1/auth/jwt/logout)
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

# Rota de Cadastro (/api/v1/auth/register)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# Rotas de Redefinição de Senha (/api/v1/auth/forgot-password, /api/v1/auth/reset-password)
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)

# Rotas de Verificação de E-mail (/api/v1/auth/request-verify-token, /api/v1/auth/verify)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

# Rotas de Usuários (/api/v1/usuarios/me, /api/v1/usuarios/{id})
users_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
