# Frontend UniLaunch

Aplicação SvelteKit 2 com Svelte 5, TypeScript, Tailwind CSS 4 e Bun.

## Desenvolvimento

Instale as dependências exclusivamente com o lockfile do Bun e inicie o servidor:

```sh
bun install --frozen-lockfile
bun run dev
```

Para abrir a aplicação automaticamente no navegador:

```sh
bun run dev -- --open
```

## Qualidade

Execute a suíte completa antes de enviar alterações:

```sh
bun run test
bun run check
bun run build
```

O projeto usa a configuração CSS do Tailwind 4. Novas classes devem seguir a nomenclatura dessa versão.

## Produção

Gere e visualize a versão de produção com:

```sh
bun run build
bun run preview
```
