# Arquitetura

O SvelteKit funciona como BFF: o navegador conversa com o SvelteKit, e o SvelteKit chama o Resource Server Rust exclusivamente no lado servidor.

## Estrutura

```text
backend/
├── migrations/          # Schema versionado do PostgreSQL
└── src/
    ├── domains/         # Features: auth e usuarios
    ├── infra/           # HMAC, senha e infraestrutura compartilhada
    ├── error.rs         # AppError e respostas seguras
    └── main.rs          # Pool, migrations, middleware e servidor

frontend/
└── src/
    ├── lib/server/      # Cliente Rust exclusivamente server-side
    ├── routes/          # Páginas, actions e proxies
    ├── hooks.server.ts  # Sessão e proteção de rotas
    └── app.d.ts         # Tipagem de locals.userId
```

## Fluxo de autenticação

```mermaid
sequenceDiagram
    actor Browser
    participant Svelte as SvelteKit (SSR/BFF)
    participant Rust as Rust/Axum
    participant DB as PostgreSQL

    Browser->>Svelte: POST /login (form action)
    Svelte->>Rust: POST /api/v1/auth/login + HMAC
    Rust->>DB: Busca usuário por e-mail
    DB-->>Rust: password_hash
    Rust->>Rust: Verifica Argon2id
    Rust->>DB: Cria sessão opaca
    Rust-->>Svelte: session_id + user_id
    Svelte-->>Browser: Cookie HttpOnly

    Browser->>Svelte: GET página protegida
    Svelte->>Rust: POST /api/v1/auth/session + HMAC
    Rust->>DB: Valida e renova quando necessário
    DB-->>Rust: user_id
    Rust-->>Svelte: user_id
    Svelte-->>Browser: SSR da página autorizada
```

## Rotas atuais

```text
POST   /api/v1/auth/login
POST   /api/v1/auth/session
DELETE /api/v1/auth/logout
POST   /api/v1/usuarios
GET    /api/v1/usuarios/{id}
```

O SvelteKit fornece `/login`, `/cadastro`, `/logout` e proxies server-side para o backend.
