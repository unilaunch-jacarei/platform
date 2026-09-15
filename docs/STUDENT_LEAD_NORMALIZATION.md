# Normalização de Leads Estudantis

## Objetivo

Normalizar instituição de ensino, curso, semestre e áreas de interesse para permitir
agrupamentos SQL estáveis sem perder os leads já coletados pela versão `0006_student_leads`.

Esta entrega usa uma estratégia expand/backfill. As colunas textuais legadas continuam
disponíveis e são preenchidas pelo backend novo. A remoção dessas colunas pertence a uma
entrega posterior, após a validação dos dados em produção.

## Regras de produto

- O semestre é opcional e, quando informado, deve ser um inteiro entre 1 e 12.
- Cada lead pode selecionar até três áreas de interesse ativas e distintas.
- Áreas de interesse são controladas pela UniLaunch e não podem ser criadas pelo formulário.
- Instituições e cursos aprovados aparecem no autocomplete público.
- Um nome inexistente pode ser enviado junto ao lead e será criado como `pending`.
- Itens `pending` ficam associados ao lead, mas não aparecem no autocomplete público.
- Cursos são categorias globais. O catálogo não afirma que uma instituição oferece o curso.
- IDs dos catálogos são UUIDs e continuam estáveis quando o nome de exibição é corrigido.

## Normalização e aliases

Cada instituição e curso possui um nome canônico e uma chave de busca única. A chave é
calculada com Unicode NFKD, remoção de diacríticos, conversão para minúsculas, remoção de
pontuação e compactação de espaços.

Aliases possuem sua própria chave normalizada e apontam para um único registro canônico.
Siglas ambíguas não devem ser cadastradas como aliases globais. Por exemplo, `Fatec` não
identifica um campus específico, enquanto `Fatec Jacareí` pode apontar para o nome canônico
desse campus.

## Contrato público

### Catálogos

- `GET /api/v1/public/leads/catalog/institutions?q=<texto>&limit=<1-20>`
- `GET /api/v1/public/leads/catalog/courses?q=<texto>&limit=<1-20>`
- `GET /api/v1/public/leads/catalog/interest-areas`

Instituições e cursos retornam somente itens `approved`. A busca considera nome canônico e
aliases, exige pelo menos dois caracteres e possui ordenação determinística. Áreas retornam
somente itens ativos.

Resposta de instituição ou curso:

```json
{
  "id": "d733f4dc-a52d-4ed8-8f05-83649acfe412",
  "name": "Faculdade de Tecnologia de Jacareí"
}
```

Resposta de área:

```json
{
  "id": "5f7f9378-f2e4-4384-9786-2193a9d87fda",
  "code": "backend",
  "name": "Backend"
}
```

### Criação de lead estudantil

Endpoint: `POST /api/v1/public/leads/students?o=<origem>`.

Payload normalizado com itens existentes:

```json
{
  "full_name": "Ada Lovelace",
  "email": "ada@example.com",
  "institution_id": "d733f4dc-a52d-4ed8-8f05-83649acfe412",
  "course_id": "64f781d8-8fca-4f81-85ae-37f0cdd73413",
  "semester_number": 3,
  "interest_area_ids": [
    "5f7f9378-f2e4-4384-9786-2193a9d87fda"
  ],
  "privacy_consent": true
}
```

Payload com novos nomes:

```json
{
  "full_name": "Ada Lovelace",
  "email": "ada@example.com",
  "institution_name": "Nova Instituição",
  "course_name": "Novo Curso",
  "semester_number": 3,
  "interest_area_ids": [],
  "privacy_consent": true
}
```

Deve ser enviada exatamente uma alternativa para instituição: `institution_id` ou
`institution_name`. A mesma regra vale para `course_id` e `course_name`.

Combinações ambíguas retornam `422`. IDs inexistentes, inativos ou pendentes enviados como
seleções públicas retornam `422`. Nomes novos são criados e associados ao lead na mesma
transação. Submissões concorrentes do mesmo nome reutilizam o registro definido pela chave
normalizada.

## Compatibilidade temporária

Durante o rollout, o backend continua aceitando o payload legado:

```json
{
  "institution_name": "Fatec Jacareí",
  "course_name": "DSM",
  "semester": "3º semestre",
  "area_of_interest": "Backend"
}
```

As regras de compatibilidade são:

- `semester` e `semester_number` não podem ser enviados juntos.
- `area_of_interest` e `interest_area_ids` não podem ser enviados juntos.
- Semestres legados só são convertidos quando contêm um único número entre 1 e 12.
- Uma área legada conhecida é associada ao catálogo; uma desconhecida permanece no campo
  legado sem criar uma nova opção pública.
- O backend novo preenche os IDs normalizados e também os campos textuais legados.
- O frontend novo envia apenas o contrato normalizado.
- Um rollback do backend continua lendo os campos antigos.

## Contrato administrativo

`LeadRead` preserva os campos legados durante a transição e adiciona:

```json
{
  "institution": {"id": "uuid", "name": "Nome", "status": "approved"},
  "course": {"id": "uuid", "name": "Nome", "status": "approved"},
  "semester_number": 3,
  "interest_areas": [{"id": "uuid", "code": "backend", "name": "Backend"}]
}
```

Endpoints de superusuário:

- `GET /api/v1/leads/catalog/institutions?status=pending`
- `PATCH /api/v1/leads/catalog/institutions/{id}/approve`
- `POST /api/v1/leads/catalog/institutions/{id}/merge`
- `GET /api/v1/leads/catalog/courses?status=pending`
- `PATCH /api/v1/leads/catalog/courses/{id}/approve`
- `POST /api/v1/leads/catalog/courses/{id}/merge`

A mesclagem transfere leads para o destino, preserva o nome anterior como alias e registra
responsável, data e destino. Automesclagem, ciclos e colisões de aliases são rejeitados.

O corpo da mesclagem informa o registro canônico:

```json
{
  "target_id": "d733f4dc-a52d-4ed8-8f05-83649acfe412"
}
```

## Ordem de rollout

1. Fazer backup e executar a migration aditiva.
2. Validar seeds, backfill e relatório de valores não convertidos.
3. Publicar o backend compatível e iniciar dual-write.
4. Executar a reconciliação para escritas feitas por pods antigos durante o rollout.
5. Publicar o frontend com os novos seletores.
6. Validar agrupamentos SQL e a quantidade de itens pendentes.
7. Manter as colunas legadas até uma entrega posterior de contract migration.

## Runbook de produção

### Antes da sincronização

1. Confirmar um backup restaurável do PostgreSQL e registrar seu identificador.
2. Confirmar que as imagens de backend e frontend pertencem ao mesmo release imutável.
3. Verificar a revisão e o volume antes do backfill:

```sql
SELECT version_num FROM alembic_version;
SELECT count(*) FROM leads WHERE lead_type = 'student';
SELECT pid, state, wait_event_type, query_start
FROM pg_stat_activity
WHERE datname = current_database() AND state <> 'idle';
```

A migration adiciona colunas anuláveis, constraints, índices e novas tabelas. Essas operações
adquirem locks de DDL no PostgreSQL. O hook atual possui `activeDeadlineSeconds: 300`; se o volume
ou as transações ativas indicarem risco de exceder esse prazo, a sincronização deve ocorrer em
janela de menor tráfego.

### Sincronização

1. Sincronizar o release pelo Argo CD.
2. Aguardar o hook `platform-database-migration` terminar com sucesso.
3. Confirmar que o backend novo ficou `Available` antes de promover ou validar o frontend.
4. Aguardar o encerramento de todos os pods do backend anterior.
5. Executar a reconciliação no ambiente do backend:

```bash
kubectl --namespace unilaunch exec deployment/platform-backend -- reconcile-student-leads
```

6. Executar o comando novamente. A saída esperada na segunda execução é
   `Reconciled 0 student leads`.
7. Validar a página `/captura-lead/aluno` em viewport desktop e mobile, incluindo busca,
   criação de novo nome, limite de áreas e uma submissão controlada.

Os manifests em `~/Repos/Apps/apps/unilaunch` já possuem o hook `PreSync`, acesso às mesmas
credenciais do backend e `INTERNAL_SECRET` no frontend. Esta alteração não exige ConfigMap,
Secret, Service, recurso adicional nem mudança nos manifests.

### Auditoria pós-rollout

Leads estudantis ainda sem referência normalizada:

```sql
SELECT id, institution_name, course_name, semester, area_of_interest, created_at
FROM leads
WHERE lead_type = 'student'
  AND (institution_id IS NULL OR course_id IS NULL)
ORDER BY created_at;
```

Itens aguardando revisão:

```sql
SELECT 'institution' AS kind, id, name, created_at
FROM educational_institutions
WHERE status = 'pending'
UNION ALL
SELECT 'course' AS kind, id, name, created_at
FROM academic_courses
WHERE status = 'pending'
ORDER BY created_at;
```

Semestres legados não convertidos:

```sql
SELECT semester, count(*) AS leads
FROM leads
WHERE lead_type = 'student'
  AND semester IS NOT NULL
  AND semester_number IS NULL
GROUP BY semester
ORDER BY leads DESC;
```

Áreas legadas sem associação normalizada:

```sql
SELECT l.area_of_interest, count(*) AS leads
FROM leads l
LEFT JOIN lead_interest_areas lia ON lia.lead_id = l.id
WHERE l.lead_type = 'student'
  AND l.area_of_interest IS NOT NULL
  AND lia.lead_id IS NULL
GROUP BY l.area_of_interest
ORDER BY leads DESC;
```

## Rollback

Se a falha estiver apenas no frontend, restaurar primeiro a imagem anterior do frontend. O
backend compatível continua aceitando o payload legado.

Se for necessário restaurar o backend anterior:

1. Interromper novas implantações e preservar o backup.
2. Restaurar o frontend anterior, que envia o contrato legado.
3. Restaurar o backend anterior.
4. Manter a revisão `0007` aplicada sempre que possível; as colunas adicionais são ignoradas pelo
   código anterior.
5. Usar `alembic downgrade 0006_student_leads` apenas se as novas tabelas impedirem a operação e
   após confirmar que não existem escritores novos.

O downgrade preserva `institution_name`, `course_name`, `semester` e `area_of_interest`, mas remove
IDs, status de revisão, aliases e associações normalizadas. Como o campo legado de área é singular,
o dual-write preserva nele somente a primeira área selecionada; as demais áreas de uma seleção
múltipla são perdidas se a revisão `0007` for removida. Por isso, o downgrade destrutivo deve ser o
último recurso e pode exigir restauração do backup.

## Remoção futura dos campos legados

Uma migration de contract só pode ser planejada quando todos estes critérios forem atendidos:

- nenhum cliente suportado envia `semester` ou `area_of_interest`;
- todos os pods e jobs em execução usam o contrato normalizado;
- a reconciliação retorna zero alterações em execuções consecutivas;
- não existem leads estudantis sem `institution_id` ou `course_id`;
- os valores legados não convertidos foram revisados ou aceitos formalmente como exceção;
- consultas e exportações usam IDs canônicos e a tabela `lead_interest_areas`;
- o período de rollback acordado para a versão anterior terminou;
- existe backup restaurável antes da remoção.

## Consultas esperadas

Os relatórios devem agrupar por IDs canônicos, usando os nomes apenas para exibição:

```sql
SELECT i.id, i.name, count(*) AS leads
FROM leads l
JOIN educational_institutions i ON i.id = l.institution_id
WHERE l.lead_type = 'student'
GROUP BY i.id, i.name
ORDER BY leads DESC;
```

Para áreas, a contagem usa a tabela associativa e cada lead participa uma vez de cada área.

Agrupamento por curso e semestre:

```sql
SELECT c.id, c.name, l.semester_number, count(*) AS leads
FROM leads l
JOIN academic_courses c ON c.id = l.course_id
WHERE l.lead_type = 'student'
GROUP BY c.id, c.name, l.semester_number
ORDER BY c.name, l.semester_number;
```

Agrupamento por área:

```sql
SELECT ia.id, ia.name, count(DISTINCT lia.lead_id) AS leads
FROM lead_interest_areas lia
JOIN interest_areas ia ON ia.id = lia.interest_area_id
GROUP BY ia.id, ia.name
ORDER BY leads DESC;
```
