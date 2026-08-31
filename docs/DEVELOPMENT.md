# Desenvolvimento local

O código deste repositório é distribuído sob a [UniLaunch Platform Source-Available Non-Commercial License](../LICENSE). Consulte a licença antes de reutilizar ou redistribuir qualquer parte do projeto.

## Stacks

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), `fastapi-users`, `uv` e PostgreSQL (ou SQLite para dev local).
- **Frontend:** SvelteKit, Svelte 5, TypeScript e Bun.
- **Segurança:** Cookies HttpOnly/Secure/SameSite Lax, JWT Bearer, Rate Limiting (SlowAPI), Argon2id e Headers OWASP.

---

## Backend

Requisitos: [uv](https://docs.astral.sh/uv/) (gerenciador rápido de pacotes Python).

```bash
cd backend
cp .env.example .env
```

Configure o arquivo `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///platform.db
JWT_SECRET=platform-dev-super-secret-jwt-key-32chars!
INTERNAL_SECRET=change-me-in-production
BIND_ADDR=0.0.0.0:8000
PUBLIC_APP_URL=http://localhost:5173
```

Para rodar o servidor em modo de desenvolvimento (com auto-reload):

```bash
uv run backend
```

A documentação interativa Swagger estará disponível em: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Frontend

Requisitos: [Bun](https://bun.sh/).

```bash
cd frontend
cp .env.example .env
bun install
bun run dev
```

Configure o arquivo `.env` do frontend:

```env
BACKEND_URL=http://127.0.0.1:8000
INTERNAL_SECRET=change-me-in-production
```

Acesse no navegador: [http://localhost:5173](http://localhost:5173).

---

## Qualidade e Testes

Para validar a formatação, o linter e a suíte completa de testes:

```bash
# Frontend
cd frontend
bun run check
bun run build

# Backend
cd backend
uv run ruff format --check .
uv run ruff check .
uv run pytest
```
