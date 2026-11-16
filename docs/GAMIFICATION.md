# Horas, níveis e conquistas

O domínio de gamificação registra o tempo efetivamente trabalhado pelo usuário e calcula seu
nível exclusivamente a partir do total de horas. Nesta primeira versão, não há limite diário e
o usuário pode manter mais de uma sessão ativa.

## Sessões de trabalho

Uma sessão pertence a um usuário e a um tipo de trabalho:

- `back`
- `front`
- `fullstack`
- `banco_de_dados`
- `api`

O contador usa intervalos. Iniciar uma sessão abre o primeiro intervalo; pausar fecha o
intervalo atual; retomar abre outro intervalo; finalizar fecha o intervalo atual e consolida a
soma dos intervalos. O tempo é armazenado em segundos, sem arredondamento de horas.

Estados possíveis:

- `active`
- `paused`
- `completed`
- `cancelled`

Sessões canceladas não geram lançamentos de horas. O usuário não edita manualmente uma sessão.

## Níveis

Os níveis são fixos nesta versão:

| Nível | Nome | Total necessário |
|---:|---|---:|
| 1 | Inicial | 0 horas |
| 2 | Básico | 10 horas |
| 3 | Mediano | 20 horas |
| 4 | Avançado | 30 horas |
| 5 | Mestre | 40 horas |

O nível máximo é Mestre. Ajustes administrativos negativos podem reduzir o total e o nível.

## Conquistas

Existem cinco conquistas fixas, uma para cada nível. A conquista Inicial é considerada
desbloqueada desde zero horas. As demais dependem do nível correspondente. Se um ajuste reduzir
o nível, as conquistas que deixarem de cumprir o requisito deixam de estar desbloqueadas.

## Ajustes administrativos

Somente superusuários podem criar ajustes. O ajuste exige:

- tipo de trabalho;
- quantidade em segundos, positiva ou negativa;
- justificativa.

Todo ajuste gera um lançamento no histórico com a origem `admin_adjustment`. O total do usuário
nunca pode ficar negativo.

## API

Sessões:

```text
POST /api/v1/gamification/work-sessions
POST /api/v1/gamification/work-sessions/{id}/pause
POST /api/v1/gamification/work-sessions/{id}/resume
POST /api/v1/gamification/work-sessions/{id}/finish
POST /api/v1/gamification/work-sessions/{id}/cancel
GET  /api/v1/gamification/work-sessions
```

Progresso do usuário:

```text
GET /api/v1/gamification/me/progress
GET /api/v1/gamification/me/hours
GET /api/v1/gamification/me/achievements
GET /api/v1/gamification/achievements
```

Operações administrativas:

```text
POST /api/v1/gamification/users/{id}/hour-adjustments
GET  /api/v1/gamification/users/{id}/progress
GET  /api/v1/gamification/users/{id}/hours
```

O contador foi separado do evento de negócio que futuramente poderá validar uma atividade,
tarefa ou Pull Request. Essa integração poderá ser adicionada sem alterar o histórico já
registrado.
