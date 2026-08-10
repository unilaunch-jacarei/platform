# Segurança

## Zero-Trust interno

O backend Rust é um Resource Server em rede privada. Ele não deve ser exposto diretamente à internet ou ao navegador. O único consumidor autorizado é o servidor SvelteKit.

## HMAC-SHA256

Cada request interna contém:

```text
x-user-id
x-timestamp
x-signature
```

O payload assinado é:

```text
{timestamp}:{caminho_da_rota}:{user_id}
```

O backend:

1. Verifica a existência e o formato dos headers.
2. Rejeita timestamps fora de uma janela de 30 segundos.
3. Recalcula HMAC-SHA256 com `INTERNAL_SECRET`.
4. Compara a assinatura em tempo constante.
5. Injeta o `user_id` autenticado na request.

Referência: [RFC 2104 — HMAC](https://www.rfc-editor.org/rfc/rfc2104).

## Senhas

Senhas são armazenadas apenas como Argon2id com salt aleatório. O valor puro nunca é logado, retornado ou salvo no banco.

## Sessões

- Tokens opacos aleatórios armazenados no PostgreSQL.
- Cookie `HttpOnly`.
- Cookie `Secure` em produção.
- `SameSite=Strict`.
- Expiração inicial de 8 horas.
- Renovação quando faltam até 30 minutos.
- Vida absoluta máxima de 24 horas.
- Logout com revogação no banco.

## SSR e segredos

O segredo interno usa `$env/dynamic/private` e só é acessado por módulos server-side do SvelteKit. As actions `+page.server.ts` processam login e cadastro no servidor. O browser não recebe `INTERNAL_SECRET` nem chama o Rust diretamente.

Referências:

- [SvelteKit — server-only modules](https://svelte.dev/docs/kit/server-only-modules)
- [SvelteKit — form actions](https://svelte.dev/docs/kit/form-actions)
- [OWASP — Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## Rate limit

O login aceita até 5 tentativas por IP a cada 60 segundos. O limite atual é local à instância Rust; em múltiplas réplicas, deve ser movido para Redis ou PostgreSQL.
