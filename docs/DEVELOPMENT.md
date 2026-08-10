# Desenvolvimento local

O código deste repositório é distribuído sob a [UniLaunch Platform Source-Available Non-Commercial License](../LICENSE). Consulte a licença antes de reutilizar ou redistribuir qualquer parte do projeto.

## Stacks

- Backend: Rust, Axum, Tokio, SQLx e PostgreSQL.
- Frontend: SvelteKit, Svelte 5, TypeScript e Bun.
- Segurança: HMAC-SHA256, Argon2id e sessões server-side.

## Backend

```bash
cd backend
cp .env.example .env
```

Configure:

```env
DATABASE_URL=postgres://postgres:postgres@127.0.0.1:5432/platform
INTERNAL_SECRET=change-me-in-production
BIND_ADDR=0.0.0.0:3000
```

Com PostgreSQL local disponível:

```bash
cargo install sqlx-cli --version 0.8.6 --no-default-features --features rustls,postgres
cargo sqlx database create
cargo sqlx migrate run
cargo sqlx prepare
SQLX_OFFLINE=true cargo build
./target/debug/backend
```

`cargo sqlx prepare` gera o cache `.sqlx/`, necessário para builds offline e CI sem PostgreSQL disponível. O cache deve ser versionado e regenerado sempre que queries ou migrations mudarem.

## Frontend

```bash
cd frontend
cp .env.example .env
bun install
bun run dev
```

```env
BACKEND_URL=http://127.0.0.1:3000
INTERNAL_SECRET=change-me-in-production
```

O segredo deve ser igual nos dois serviços. Em Docker, use o nome do serviço, por exemplo `BACKEND_URL=http://backend:3000`.

## Qualidade

```bash
cd frontend && bun run check
cd ../backend && cargo fmt --all -- --check
SQLX_OFFLINE=true cargo test
```
