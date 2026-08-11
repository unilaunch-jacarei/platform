# Backlog de implementação

Este documento transforma o roadmap em tarefas executáveis. A ordem considera as dependências entre banco, backend, SSR e interface.

## Sprint 1 — fechamento de Auth, UX e fundação

### S1-01 — Inventário visual do `base_estilo`

- [ ] Mapear os componentes React existentes em `base_estilo/src/app/components`.
- [ ] Separar padrões visuais de componentes específicos de tela.
- [ ] Definir tokens de cor, tipografia, espaçamento, borda, sombra e estados.
- [ ] Registrar no frontend um contrato de componentes reutilizáveis.

**Aceite:** o time consegue implementar uma nova tela usando os mesmos tokens sem copiar CSS de login.

### S1-02 — Design system reutilizável em Svelte

- [ ] Criar `frontend/src/lib/components/ui/`.
- [ ] Migrar para Svelte os componentes necessários: `Button`, `Input`, `PasswordInput`, `Label`, `Card`, `Alert`, `Spinner`, `Modal`, `Toast`, `Badge`, `Select` e `EmptyState`.
- [ ] Usar snippets/props tipadas e estados `disabled`, `loading`, `error` e `success`.
- [ ] Criar uma página interna de preview dos componentes.
- [ ] Remover estilos duplicados de login/cadastro depois da migração.

**Aceite:** login e cadastro usam exclusivamente componentes do design system e funcionam em desktop e mobile.

### S1-03 — Refinar login e cadastro

- [ ] Aplicar os componentes e tokens do `base_estilo`.
- [ ] Adicionar validação server-side e mensagens acessíveis.
- [ ] Garantir estado de carregamento sem submissão duplicada.
- [ ] Garantir que senha nunca apareça em logs, URL, resposta ou `locals`.
- [ ] Adicionar testes de action para sucesso, credenciais inválidas e backend indisponível.

**Aceite:** os formulários permanecem server-side e não expõem `INTERNAL_SECRET`.

### S1-04 — Recuperação de senha com Resend

- [ ] Criar migration `password_reset_tokens` com `token_hash`, `usuario_id`, `expires_at`, `used_at` e timestamps.
- [ ] Criar endpoint para solicitar recuperação sem revelar se o e-mail existe.
- [ ] Gerar token aleatório, armazenar somente seu hash e limitar validade a 30 minutos.
- [ ] Integrar envio pelo Resend exclusivamente em módulo server-side.
- [ ] Criar página `/recuperar-senha`.
- [ ] Criar página `/redefinir-senha?token=...`.
- [ ] Invalidar token após o primeiro uso e revogar sessões existentes após redefinição.
- [ ] Aplicar rate limit por IP e e-mail normalizado.

**Aceite:** o endpoint sempre responde de forma genérica; token expirado, usado ou inválido não permite alteração de senha.

### S1-05 — Fundação operacional

- [ ] Adicionar `RESEND_API_KEY`, `MAIL_FROM` e `PUBLIC_APP_URL` apenas nos ambientes server-side.
- [ ] Adicionar testes de segurança para HMAC, Argon2id, sessão e reset.
- [ ] Configurar CI com `cargo fmt`, `cargo test`, `cargo sqlx prepare`/cache e `bun run check`.
- [ ] Revisar secrets, `.gitignore`, licença e documentação de contribuição.

**Definition of Done do Sprint 1:** autenticação, logout, sessão, recuperação de senha, UI reutilizável, testes e CI documentados.

## Sprint 2 — Boards, Kanban, tarefas e auditoria

### S2-01 — Modelagem de Boards

- [ ] Criar domínio `backend/src/domains/boards/`.
- [ ] Criar migration `boards` com `id`, `nome`, `slug`, `descricao`, `owner_id`, status e timestamps.
- [ ] Criar associação de membros/permissões do board.
- [ ] Definir autorização: owner, admin, contributor e viewer.
- [ ] Criar CRUD server-side com queries SQLx verificadas.

**Aceite:** somente membros autorizados conseguem visualizar ou alterar um board.

### S2-02 — Colunas fixas do Kanban

- [ ] Criar `board_columns` com `board_id`, `column_key`, `name`, `position` e timestamps.
- [ ] Definir conjunto inicial fixo: `backlog`, `todo`, `in_progress`, `review` e `done`.
- [ ] Criar as colunas automaticamente na criação do board.
- [ ] Impedir criação e remoção arbitrária no MVP.
- [ ] Permitir apenas alteração controlada de nome/posição, se aprovada pela regra do produto.
- [ ] Garantir unicidade de `board_id + column_key`.

**Aceite:** toda task pertence a exatamente uma coluna válida e não existem colunas órfãs.

### S2-03 — Tasks

- [ ] Criar `tasks` com título, descrição, board, coluna, posição, criador, responsável, prioridade e timestamps.
- [ ] Usar ordenação estável para movimentação, evitando colisões de posição.
- [ ] Criar endpoints de criação, edição, consulta, arquivamento e movimentação.
- [ ] Validar autorização por board em todos os endpoints.
- [ ] Não permitir alteração direta de `created_by` ou histórico.

**Aceite:** criar, editar, mover, atribuir, arquivar e listar tasks sem perder o histórico.

### S2-04 — Auditoria imutável de tasks

- [ ] Criar `task_audit_events` com ator, task, board, tipo, `before_data`, `after_data`, metadata e timestamp.
- [ ] Registrar criação, edição de título, descrição, prioridade, responsável, coluna, posição e arquivamento.
- [ ] Registrar o motivo e o contexto da movimentação quando fornecidos.
- [ ] Escrever o evento na mesma transação da alteração da task.
- [ ] Impedir update/delete de eventos pela API normal.
- [ ] Criar endpoint paginado de histórico por task.

**Aceite:** toda alteração relevante gera exatamente um evento auditável e o frontend consegue renderizar quem fez o quê e quando.

### S2-05 — Mensagens e comentários

- [ ] Definir no MVP mensagens como comentários ligados a uma task.
- [ ] Criar `task_comments` com autor, conteúdo, timestamps e soft delete.
- [ ] Criar endpoints paginados de listar, criar, editar e remover comentário próprio.
- [ ] Auditar criação, edição e remoção de comentários.
- [ ] Definir limite de tamanho e sanitização de conteúdo.

**Aceite:** comentários aparecem na task, respeitam autorização e deixam trilha de auditoria.

### S2-06 — UI Board/Kanban

- [ ] Criar componentes `BoardHeader`, `Column`, `TaskCard`, `TaskDialog`, `TaskDetails`, `ActivityTimeline`, `CommentComposer` e `MemberAvatar`.
- [ ] Implementar carregamento SSR e mutations via actions/server endpoints.
- [ ] Implementar movimentação com feedback otimista e rollback em erro.
- [ ] Mostrar timeline de auditoria em cada task.
- [ ] Mostrar estado vazio, loading, erro e permissão insuficiente.

**Aceite:** o board funciona sem chamada direta do browser ao Rust e cada alteração visível tem feedback de sucesso/erro.

### S2-07 — Testes e segurança do domínio

- [ ] Testar autorização por papel e por board.
- [ ] Testar transação task + auditoria.
- [ ] Testar movimentação entre colunas.
- [ ] Testar concorrência básica e posições.
- [ ] Testar paginação e ordenação do histórico.
- [ ] Testar XSS/sanitização em comentários e descrição.

**Definition of Done do Sprint 2:** board funcional, colunas fixas, tasks, mensagens, auditoria imutável e frontend SSR integrado.

## Decisões pendentes antes de implementar S2

1. Confirmar se “mensagens” significa comentários em tasks ou mensagens gerais do board.
2. Confirmar os papéis e permissões definitivos.
3. Confirmar se colunas podem renomear/reordenar ou se são totalmente imutáveis.
4. Confirmar regras de exclusão: soft delete para tasks, comentários e boards.
5. Definir retenção e exportação do histórico de auditoria.
