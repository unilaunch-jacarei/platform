# Como contribuir

Obrigado pelo interesse em construir o UniLaunch Platform.

## Antes de começar

1. Abra uma issue descrevendo a ideia ou o problema.
2. Para mudanças maiores, aguarde a definição do escopo antes de implementar.
3. Nunca envie `.env`, credenciais, tokens, dumps de banco ou dados pessoais.

## Pull requests

- Use uma branch específica para a mudança.
- Mantenha o escopo pequeno e explique a motivação.
- Execute `cargo fmt --all -- --check` e `SQLX_OFFLINE=true cargo test` no backend.
- No PowerShell (Windows), use `$env:SQLX_OFFLINE="true"` antes de executar `cargo test`.
- Execute `bun run check` no frontend.
- Atualize migrations e o cache SQLx quando alterar queries.
- Não inclua segredos ou dados reais nos testes.

## Comunicação

Use as [Issues](https://github.com/unilaunch-jacarei/platform/issues) e [Discussions](https://github.com/unilaunch-jacarei/platform/discussions). Para assuntos privados, escreva para [unilaunchorg@gmail.com](mailto:unilaunchorg@gmail.com).
