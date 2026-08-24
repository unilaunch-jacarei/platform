# Componentes React UniLaunch

Biblioteca independente baseada em Atomic Design para as telas do prototipo React.

```tsx
import { AuthLayout, LoginForm, ProjectCard } from '../react-components/src';
```

- `atoms.tsx`: componentes visuais basicos.
- `molecules.tsx`: combinacoes reutilizaveis de atomos.
- `organisms.tsx`: formularios, shell, perfil, feed, notificacoes e Kanban.
- `templates.tsx`: estruturas de pagina.

O frontend atual de `platform/frontend` usa SvelteKit. Esta biblioteca React nao e importada diretamente pelas rotas Svelte; ela deve ser consumida por um app React ou por uma migracao planejada do frontend.
