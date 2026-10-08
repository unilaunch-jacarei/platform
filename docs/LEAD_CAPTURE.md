# Captura Pública de Leads

## Escopo

O formulário é público e captura um contato interessado para posterior contato comercial.
O visitante não precisa de conta. O usuário autenticado da plataforma não será associado ao
lead nesta primeira versão.

## Dados do formulário

### Contato

- `full_name`: obrigatório, 2 a 255 caracteres
- `email`: obrigatório, válido e normalizado para minúsculas

### Empresa

- `company_name`: obrigatório, 2 a 255 caracteres
- `job_title`: opcional, até 120 caracteres
- `company_size`: opcional, enum definido pela API
- `website`: opcional, URL válida
- `message`: opcional, até 2.000 caracteres

### Estudante

- `institution_id` ou `institution_name`: exatamente uma das alternativas
- `course_id` ou `course_name`: exatamente uma das alternativas
- `semester_number`: opcional, inteiro entre 1 e 12
- `interest_area_ids`: zero a três UUIDs distintos de áreas ativas
- `linkedin_url` e `github_url`: opcionais, URLs válidas
- `message`: opcional, até 2.000 caracteres

O contrato normalizado, a compatibilidade temporária e a operação dos catálogos estão em
[`STUDENT_LEAD_NORMALIZATION.md`](./STUDENT_LEAD_NORMALIZATION.md).

### Consentimento

- `privacy_consent`: obrigatório e deve ser `true`
- `privacy_consent_at`: preenchido pelo backend
- `privacy_policy_version`: versão `v1.0`, preenchida pelo backend

Não serão aceitos `owner_id`, status, timestamps ou campos internos enviados pelo cliente.

## Origem

O parâmetro `o` aceita qualquer string enviada a ele.
Quando ausente ou vazia, a origem será `direct`. O valor persistido será limitado a 255 caracteres.
A origem será persistida no lead e em cada evento de visualização.

## Visualizações

Cada carregamento bem-sucedido da página pública gera um evento de visualização antes da
exibição do formulário. O evento contém apenas origem e timestamp. Não haverá contador
mutável no formulário nesta versão.

O endpoint de visualização será idempotente por requisição do BFF, usando uma chave de evento
gerada no server-side. Repetições com a mesma chave não criam eventos duplicados.

## Duplicidade e status

Leads com o mesmo e-mail normalizado serão aceitos novamente, pois podem representar contatos
ou campanhas diferentes. A API retornará `201` para cada submissão válida.

O status inicial será `new`. Os status administrativos serão `new`, `contacted`, `qualified`,
`converted` e `discarded`.

## API prevista

- `POST /api/v1/public/leads/views?o=...`: registra visualização e retorna `204`
- `POST /api/v1/public/leads?o=...`: cria lead e retorna `201`
- `POST /api/v1/public/leads/students?o=...`: cria lead estudantil e retorna `201`
- `GET /api/v1/public/leads/catalog/institutions?q=...`: pesquisa instituições aprovadas
- `GET /api/v1/public/leads/catalog/courses?q=...`: pesquisa cursos aprovados
- `GET /api/v1/public/leads/catalog/interest-areas`: lista áreas ativas
- `GET /api/v1/leads`: lista leads para um superusuário
- `GET /api/v1/leads/{id}`: consulta um lead para um superusuário
- `PATCH /api/v1/leads/{id}/status`: altera status do lead
- `DELETE /api/v1/leads/{id}`: exclui um lead

As rotas públicas não expõem dados administrativos nem exigem autenticação.

## Privacidade e retenção

O conteúdo do lead não será escrito em logs. O prazo padrão de retenção é de 365 dias e pode
ser configurado por `LEAD_RETENTION_DAYS`. O comando `purge-leads` remove registros vencidos e
deve ser agendado pela infraestrutura. Superusuários também podem excluir um lead pela API.
O consentimento e a versão da política serão armazenados junto ao lead para auditoria.

## Observabilidade

O endpoint `/metrics` exige `Authorization: Bearer <METRICS_TOKEN>` em staging e produção.
As métricas RED contabilizam respostas `4xx` e `5xx` por método, rota e classe de status.
