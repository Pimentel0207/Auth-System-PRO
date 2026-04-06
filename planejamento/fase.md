# Fases do Desenvolvimento: Auth System PRO

O projeto será construído seguindo um roteiro lógico de evolução técnica.

## 🛠️ Fase 0: Dev Experience & Infra (Production-Ready)
- [ ] Configuração do **Docker** e **Docker Compose** (API, Postgres, Redis).
- [ ] Setup do **Pyproject.toml** com **Ruff** (Linter) e **Mypy** (Types).
- [ ] Configuração de **Pre-commit hooks** para garantir qualidade no commit.
- [ ] Estrutura inicial de pastas (`src/`, `tests/`, `alembic/`).

## 🏗️ Fase 1: Fundação e Cadastro
- [ ] Setup do ambiente (FastAPI + SQLModel + **Alembic**).
- [ ] Modelagem do banco: `users`, `refresh_tokens`, `password_reset_tokens`, `activity_logs`.
- [ ] Migrações iniciais via Alembic.
- [ ] Implementação da rota `POST /register`.
- [ ] Hashing de senhas com **Argon2** (`argon2-cffi`).

## 🔐 Fase 2: O Coração (Autenticação)
- [ ] Implementação da rota `POST /login`:
  - Verificação de hash Argon2.
  - Geração de **Access Token** (JWT via `PyJWT`, 30min).
  - Geração de **Refresh Token** (UUID, 7 dias) em **Cookie HttpOnly/Secure/SameSite=Strict**.
  - Registro em `ActivityLogs`.

## 🛡️ Fase 3: Proteção e Sessão (Nível Sênior)
- [ ] Middleware de proteção de rotas — valida JWT + verifica `is_active` do usuário.
- [ ] Rota `GET /me` — retorna dados do usuário autenticado.
- [ ] Rota `POST /refresh` — valida refresh token no banco, **rotaciona** (invalida antigo, emite novo), detecta reuso malicioso.
- [ ] Rota `POST /logout` — revoga refresh token no banco (`revogado = true`).

## 🔄 Fase 4: Fluxos de Recuperação
- [ ] Implementação de `forgot-password` (Geração de token de reset).
- [ ] Implementação de `reset-password` (Validação e troca de senha).

## 🔥 Fase 5: Resiliência e Refinamento
- [ ] **Handler Global de Exceções** (Respostas de erro padronizadas).
- [ ] Rate Limiting (Limitar tentativas de login).
- [ ] Sistema de Logs de atividade (Sucesso/Falha/IP).

## 🧪 Fase 6: Qualidade & CI/CD
- [ ] Implementação de **Testes Unitários** e **Integração** com **Pytest**.
- [ ] Configuração de **GitHub Actions** (CI) para testes automáticos.
- [ ] Documentação final da API (Swagger Customizado).
- [ ] Preparação para Deploy (Configurações de Produção).


