# Estrutura do Sistema

## 🧩 Rotas da API (Interface)

| Método | Rota | Descrição | Segurança |
| :--- | :--- | :--- | :--- |
| `POST` | `/register` | Criação de novo usuário | - |
| `POST` | `/login` | Autenticação e recebimento de tokens | **Set-Cookie (HttpOnly)** |
| `POST` | `/refresh` | Renova o Access Token | **Cookie-based** |
| `POST` | `/logout` | Encerra a sessão ativa | **Blacklist Add** |
| `GET` | `/me` | Retorna dados do usuário logado | JWT Header |
| `POST` | `/forgot-password` | Solicita link de recuperação | - |
| `POST` | `/reset-password` | Define nova senha com token | JWT/Token |

## ⚙️ Fluxo de Funcionamento (Nível Sênior)

1. **Login:** Verificação de hash Argon2 → access token (JWT, 30min) retornado no body + refresh token (UUID opaco, 7 dias) em **Cookie HttpOnly/Secure/SameSite=Strict** (protege contra XSS e CSRF).

2. **Access Token:** Enviado pelo cliente no header `Authorization: Bearer <token>`. Curta duração — não requer blacklist.

3. **Refresh:** Cliente envia o cookie com o refresh token → backend valida no banco → **invalida o token antigo** e emite um novo par (access + refresh). Reuso de token já invalidado indica sessão roubada: todos os tokens do usuário são revogados.

4. **Logout:** Backend marca o refresh token como `revogado = true` no banco. Access token expira naturalmente em até 30min — sem custo de consulta ao Redis por requisição.

5. **Bloqueio imediato (casos críticos):** Se um admin bloquear um usuário, o `is_active = false` é verificado em cada requisição — nenhum access token válido funciona para usuários bloqueados.

6. **Erros:** Um **ExceptionHandler** captura erros de banco ou lógica e retorna um JSON padronizado para o frontend.

## 🏗️ Estrutura de Arquivos (Layout Profissional)

```text
/auth-system-pro
├── src/                # Código fonte da aplicação
│   ├── api/            # Rotas (Endpoints) e Controladores
│   ├── core/           # Lógica de negócio e Segurança
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Schemas Pydantic (Validação)
│   └── main.py         # Entrypoint FastAPI
├── tests/              # Testes unitários e integração (Pytest)
├── alembic/            # Migrações planificadas do banco
├── .env                # Segredos e variáveis de ambiente (Não comitado)
├── Dockerfile          # Receita da imagem da API
├── docker-compose.yml  # Orquestração (API + Postgres + Redis)
└── pyproject.toml      # Configs de Ruff, Mypy e dependências
```

## 🧩 Rotas da API (Interface)

| Método | Rota | Descrição | Segurança |
| :--- | :--- | :--- | :--- |
| `POST` | `/register` | Criação de novo usuário | Pydantic Validation |
| `POST` | `/login` | Autenticação e tokens | **HttpOnly Cookie** |
| `POST` | `/refresh` | Renova Access Token | **Cookie-based** |
| `POST` | `/logout` | Invalida sessão ativa | **Blacklist Add** |
| `GET` | `/me` | Dados do usuário logado | JWT Bearer |

## ⚙️ Plano de Testes (Pytest)
1. **Unit:** Validação de hashes e geração de payloads JWT.
2. **Integration:** Fluxo completo de Registro -> Login -> Acesso Protegido.
3. **Security:** Tentativa de acesso com token expirado ou na blacklist.

## 🗄️ Modelo de Dados (Schema)

### Users
- `id` (UUID), `email` (Unique), `password_hash` (Argon2), `role` (admin, user), `is_active`, `created_at`.

### RefreshTokens (PostgreSQL)
- `id` (UUID), `user_id` (FK), `token_hash` (Argon2 do token — nunca texto claro), `revogado` (bool), `expira_em`, `ip_address`, `user_agent`, `criado_em`.

### PasswordResetTokens (PostgreSQL)
- `id` (UUID), `user_id` (FK), `token_hash`, `usado` (bool), `expira_em` (15min), `criado_em`.

### ActivityLogs (PostgreSQL — append-only)
- `id`, `user_id`, `action` (LOGIN, LOGOUT, REGISTER, RESET_PASSWORD, etc.), `ip_address`, `user_agent`, `status` (success, failure), `timestamp`.


