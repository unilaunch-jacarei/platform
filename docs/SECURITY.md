# Segurança

## Zero-Trust interno

O backend Python/FastAPI é um Resource Server em rede privada. Ele não deve ser exposto diretamente à internet ou ao navegador. O único consumidor autorizado é o servidor SvelteKit (BFF).

## Autenticação interna

O SvelteKit autentica no backend com JWT Bearer:

```text
Authorization: Bearer <access_token>
```

O token é emitido por `POST /api/v1/auth/jwt/login` (fastapi-users) e armazenado pelo BFF em cookie `HttpOnly`. O navegador nunca recebe o token nem chama o backend diretamente.

### Assinatura do IP do cliente

Para o rate limit usar o IP real atrás do proxy, o BFF envia:

```text
X-Client-IP
X-Client-IP-Signature
```

A assinatura é `HMAC-SHA256(INTERNAL_SECRET, client_ip)`. O backend ([`backend/infra/limiter.py`](../backend/src/backend/infra/limiter.py)) só aceita o IP encaminhado quando ele é um IP válido e a assinatura confere em tempo constante; caso contrário, usa o IP da conexão.

## Senhas

Senhas são armazenadas apenas como hash Argon2id (via fastapi-users/pwdlib). O valor puro nunca é logado, retornado ou salvo no banco.

## Sessões

- JWT com validade de 7 dias (`JWT_LIFETIME_SECONDS`), emitido pelo backend.
- Cookie `session_token` `HttpOnly` e `SameSite=Lax`.
- Cookie `Secure` fora do ambiente de desenvolvimento.
- Logout remove o cookie no BFF e chama `POST /api/v1/auth/jwt/logout`.
- O backend não mantém sessão em banco; a validade é a do JWT.

## SSR e segredos

O segredo interno usa `$env/dynamic/private` e só é acessado por módulos server-side do SvelteKit. As actions `+page.server.ts` processam login e cadastro no servidor. O browser não recebe `INTERNAL_SECRET` nem chama o backend diretamente.

## Rate limit

Limites aplicados hoje (SlowAPI) nos endpoints públicos de captura de leads:

- `POST /api/v1/public/leads/views`: 30/minuto
- `POST /api/v1/public/leads`: 5/hora
- `POST /api/v1/public/leads/students`: 5/hora
- `GET /api/v1/public/leads/catalog/*`: 60/minuto

O login ainda não possui rate limit dedicado. Em múltiplas réplicas o storage compartilhado deve usar Redis (`RATE_LIMIT_STORAGE_URI`).
