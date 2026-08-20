# Arquitetura Hexagonal (Ports & Adapters)

Este documento descreve a arquitetura do backend em Rust, a separação de responsabilidades entre as camadas, a direção das dependências e o passo a passo para estender o sistema com novas funcionalidades ou novos módulos.

---

## 1. Princípios e Regra de Dependência

A arquitetura segue rigorosamente o padrão **Ports & Adapters (Hexagonal Architecture)** com injeção de dependências explícita.

### Direção das Dependências

```text
Adapters (Inbound / Outbound)
         ↓
    Application
         ↓
       Domain
```

* **Domain**: Não conhece nenhuma camada externa. Não depende de Axum, SQLx, Tokio, Serde, HTTP ou banco de dados. Contém apenas entidades puras, value objects, invariantes e erros de negócio.
* **Application**: Conhece apenas o Domain. Define casos de uso (`UseCases`) e contratos de capacidades externas (`Ports` / `traits`). Não conhece implementações concretas de banco de dados, HTTP ou bibliotecas de terceiros.
* **Adapters**:
  * **Inbound (HTTP/Axum)**: Traduz requests HTTP, DTOs e rotas em comandos da aplicação e invoca os use cases. O `AppState` contém apenas instâncias de Use Cases (`Arc<UseCase>`), nunca repositórios ou pools de conexão diretamente.
  * **Outbound (PostgreSQL, Argon2, Resend, etc.)**: Implementa os ports definidos pela camada de aplicação.
* **Bootstrap (Composition Root)**: O único local da aplicação autorizado a conhecer todas as implementações concretas. É responsável por instanciar a infraestrutura, montar o grafo de dependências e configurar o servidor.
* **Main**: Ponto de entrada mínimo (~20 linhas) que lê a configuração e delega a inicialização para o `bootstrap`.

---

## 2. Estrutura de Diretórios

```text
backend/src/
├── domain/                                 # 1. Regras de Negócio Puras (Pure Rust)
│   ├── mod.rs
│   ├── usuarios/
│   │   ├── mod.rs
│   │   ├── entity.rs                       # Entidade Usuario
│   │   ├── value_objects.rs                # UsuarioId, Nome, Email, PlainPassword, HashedPassword
│   │   └── error.rs                        # UsuarioDomainError
│   └── auth/
│       ├── mod.rs
│       ├── entity.rs                       # Entidade Session
│       ├── value_objects.rs                # SessionId, RawResetToken, ResetTokenHash
│       └── error.rs                        # AuthDomainError
│
├── application/                            # 2. Casos de Uso & Contratos (Ports)
│   ├── mod.rs
│   ├── usuarios/
│   │   ├── mod.rs
│   │   ├── ports.rs                        # Trait: UsuarioRepository
│   │   ├── create_usuario.rs               # CreateUsuarioUseCase & Command
│   │   ├── get_usuario.rs                  # GetUsuarioUseCase
│   │   └── error.rs                        # UsuarioAppError
│   └── auth/
│       ├── mod.rs
│       ├── ports.rs                        # Traits: AuthRepository, PasswordHasher, EmailSenderPort, etc.
│       ├── login.rs                        # LoginUseCase & Command
│       ├── session.rs                      # ValidateSessionUseCase
│       ├── logout.rs                       # LogoutUseCase
│       ├── reset_password.rs               # RequestPasswordResetUseCase & Command
│       ├── confirm_reset_password.rs       # ConfirmPasswordResetUseCase & Command
│       └── error.rs                        # AuthAppError
│
├── adapters/                               # 3. Adaptadores de Entrada e Saída
│   ├── mod.rs
│   ├── inbound/                            # Inbound: Axum HTTP
│   │   ├── mod.rs
│   │   └── http/
│   │       ├── mod.rs
│   │       ├── router.rs                   # Router raiz com rotas e middleware HMAC
│   │       ├── state.rs                    # AppState com agrupamento de use cases
│   │       ├── error.rs                    # ApiError (mapeamento HTTP 400, 401, 404, 422, 500)
│   │       ├── middleware/
│   │       │   └── hmac.rs                 # Verificação de requisição autenticada do BFF
│   │       ├── usuarios/
│   │       │   ├── dto.rs                  # CreateUsuarioRequest, UsuarioResponse, UsuarioEnvelope
│   │       │   ├── handlers.rs             # Handlers Axum
│   │       │   └── routes.rs               # Rotas /api/v1/usuarios
│   │       └── auth/
│   │           ├── dto.rs                  # LoginRequest, LoginResponse, ResetPasswordRequest, etc.
│   │           ├── handlers.rs             # Handlers Axum
│   │           └── routes.rs               # Rotas /api/v1/auth/*
│   │
│   └── outbound/                           # Outbound: Implementação dos Ports
│       ├── mod.rs
│       ├── persistence/
│       │   └── postgres/
│       │       ├── models.rs               # Modelos relacionais SQLx
│       │       ├── usuario_repository.rs   # PostgresUsuarioRepository (impl UsuarioRepository)
│       │       └── auth_repository.rs      # PostgresAuthRepository (impl AuthRepository)
│       ├── security/
│       │   ├── argon2_hasher.rs            # Argon2PasswordHasher (impl PasswordHasher)
│       │   └── token_generator.rs          # CryptoTokenGenerator (impl ResetTokenGenerator, SessionIdGenerator)
│       ├── email/
│       │   └── resend_sender.rs            # ResendEmailSender (impl EmailSenderPort)
│       └── rate_limiter/
│           └── memory_limiter.rs           # MemoryRateLimiter (impl RateLimiterPort)
│
├── bootstrap/                              # 4. Composition Root
│   ├── mod.rs
│   ├── config.rs                           # Leitura de variáveis de ambiente (AppConfig)
│   └── container.rs                        # Instanciação e injeção explícita de dependências
│
├── lib.rs
└── main.rs
```

---

## 3. Guia: Como Adicionar uma Nova Funcionalidade (Use Case)

Exemplo: Adicionar um caso de uso para **Atualizar o Perfil do Usuário** (`UpdateUserProfile`).

### Passo 1: Domínio (`src/domain/usuarios/`)
1. Se necessário, crie novos Value Objects ou adicione métodos de validação/mutação na entidade `Usuario` (ex: `Biografia`, `Telefone`).
2. Garanta que todas as regras de negócio invariantes estejam protegidas nos Value Objects/Entidade.

### Passo 2: Ports & Contrato (`src/application/usuarios/ports.rs`)
1. Adicione o método necessário no trait do repositório:
   ```rust
   #[async_trait]
   pub trait UsuarioRepository: Send + Sync {
       // ... métodos existentes ...
       async fn update(&self, user: &Usuario) -> Result<(), RepositoryError>;
   }
   ```

### Passo 3: Caso de Uso (`src/application/usuarios/update_profile.rs`)
1. Crie a struct de comando e a struct do caso de uso com suas dependências:
   ```rust
   pub struct UpdateProfileCommand {
       pub user_id: i64,
       pub nome: String,
   }

   pub struct UpdateProfileUseCase {
       repository: Arc<dyn UsuarioRepository>,
   }

   impl UpdateProfileUseCase {
       pub fn new(repository: Arc<dyn UsuarioRepository>) -> Self {
           Self { repository }
       }

       pub async fn execute(&self, cmd: UpdateProfileCommand) -> Result<(), UsuarioAppError> {
           let mut user = self.repository
               .find_by_id(UsuarioId::new(cmd.user_id))
               .await?
               .ok_or(UsuarioAppError::UsuarioNaoEncontrado(cmd.user_id))?;

           user.nome = Nome::new(cmd.nome)?;
           self.repository.update(&user).await?;
           Ok(())
       }
   }
   ```
2. Adicione testes unitários no próprio arquivo usando um `FakeUsuarioRepository` em memória.

### Passo 4: Outbound Adapter (`src/adapters/outbound/persistence/postgres/usuario_repository.rs`)
1. Implemente o método `update` com a query SQLx necessária.

### Passo 5: Inbound Adapter (`src/adapters/inbound/http/usuarios/`)
1. **DTO** (`dto.rs`): Defina `UpdateProfileRequest`.
2. **Handler** (`handlers.rs`): Crie a função do handler Axum que extrai os parâmetros, chama `state.user_use_cases.update_profile.execute(cmd)` e retorna o status HTTP adequado.
3. **Rotas** (`routes.rs`): Adicione a rota `.route("/api/v1/usuarios/{id}", put(handlers::update_profile))`.

### Passo 6: Bootstrap & AppState (`src/adapters/inbound/http/state.rs` e `src/bootstrap/container.rs`)
1. Adicione o campo `pub update_profile: Arc<UpdateProfileUseCase>` em `UserUseCases` dentro de `state.rs`.
2. Em `container.rs`, instancie `let update_profile = Arc::new(UpdateProfileUseCase::new(usuario_repo.clone()));` e repasse para o `AppState`.

---

## 4. Guia: Como Adicionar um Novo Domínio/Módulo Completo

Exemplo: Criar o módulo de **Projetos** (`projetos`).

```text
1. src/domain/projetos/
   ├── mod.rs
   ├── entity.rs               # Projeto, ProjetoId, etc.
   ├── value_objects.rs        # Titulo, Descricao, etc.
   └── error.rs                # ProjetoDomainError

2. src/application/projetos/
   ├── mod.rs
   ├── ports.rs                # ProjetoRepository
   ├── create_projeto.rs       # CreateProjetoUseCase
   ├── list_projetos.rs        # ListProjetosUseCase
   └── error.rs                # ProjetoAppError

3. src/adapters/outbound/persistence/postgres/projeto_repository.rs
   # Impl PostgresProjetoRepository para ProjetoRepository

4. src/adapters/inbound/http/projetos/
   ├── mod.rs
   ├── dto.rs                  # CreateProjetoRequest, ProjetoResponse
   ├── handlers.rs             # Handlers Axum
   └── routes.rs               # Router Axum para /api/v1/projetos

5. Conectar no Router raiz e no AppState
   - adapters/inbound/http/state.rs: Adicionar ProjetoUseCases ao AppState
   - adapters/inbound/http/router.rs: Adicionar .merge(projetos::router())
   - bootstrap/container.rs: Instanciar PostgresProjetoRepository e os UseCases
```

---

## 5. Estratégia de Testes

### 1. Testes Unitários de Casos de Uso (Sem I/O)
* **Vantagem**: Executam em milissegundos, sem precisar de banco de dados, Docker ou rede.
* **Como fazer**: Crie structs que implementem os traits dos ports com coleções em memória (`Mutex<Vec<_>>`, `Mutex<HashMap<_, _>>`) e injete-os diretamente no caso de uso.

### 2. Testes de Domínio e Value Objects
* Testam invariantes, regras de formatação e limites diretamente nos métodos construtores dos Value Objects.

### 3. Testes de Integração de Fluxo Completo (`tests/`)
* Testam a composição real com banco de dados PostgreSQL e migrations ativas, validando queries SQL, transações e idempotência.
