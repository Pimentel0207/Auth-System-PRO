# 🔐 Auth System PRO v0.2.0

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens" alt="JWT">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

### 🚀 O "Porteiro Digital" Inteligente
O **Auth System PRO** é um **Serviço Central de Autenticação** de nível empresarial. Projetado para ser a espinha dorsal de segurança de ecossistemas modernos, permite que aplicações Web, Mobile e SaaS deleguem a gestão de identidade a um núcleo robusto e altamente seguro.

---

## 📋 Sumário
- [🎯 O Conceito](#-o-conceito)
- [🛠️ Stack Tecnológica](#️-stack-tecnológica)
- [🔥 Diferenciais Técnicos](#-diferenciais-técnicos)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [🚀 Endpoints da API](#-endpoints-da-api)
- [⚡ Quickstart](#-quickstart)

---

## 🎯 O Conceito
Imagine um serviço universal que qualquer aplicação pode interrogar:
> **Aplicação Client:** "Este usuário com este token é confiável?"  
> **Auth System:** "Sim, é o Usuário X e ele possui as permissões Y. Acesso garantido."

### Objetivos:
1. **Universalidade:** Integração transparente com qualquer plataforma.
2. **Escalabilidade:** Controle de sessões otimizado para alta demanda.
3. **Profissionalismo:** Arquitetura limpa seguindo os melhores padrões da indústria.

---

## 🛠️ Stack Tecnológica
| Camada | Tecnologia | Função |
| :--- | :--- | :--- |
| **Backend** | FastAPI (Async) | Framework de alta performance |
| **Segurança** | Argon2 + PyJWT | Hashing e tokens JWT |
| **ORM** | SQLModel + SQLAlchemy | Modelos e queries assíncronos |
| **Banco** | PostgreSQL 16 | Persistência de dados |
| **Migrations** | Alembic | Versionamento do schema |
| **Container** | Docker + Compose | Ambientes isolados |
| **QA** | Pytest + Ruff + Mypy | Testes, linter e tipagem |

---

## 🔥 Diferenciais Técnicos (v0.2.0)

- 🏗️ **Service Layer Pattern** — Lógica de negócio isolada das rotas HTTP
- 🛡️ **Token Rotation com Reuse Detection** — Se um refresh token revogado for reutilizado, TODOS os tokens do usuário são invalidados automaticamente
- 🔑 **JWT com `jti` (JWT ID)** — Cada token é único, prevenindo colisões
- 🔐 **RBAC** — Role-Based Access Control com dependency `require_admin`
- 🌐 **CORS Configurável** — Origens permitidas via variável de ambiente
- 🔄 **Refresh Token Rotation** — Cada uso emite um novo par de tokens
- 📝 **Audit Trail Completo** — Todas as ações são logadas com IP e User-Agent
- ⚙️ **Exception Handling Global** — Respostas padronizadas e seguras
- 🐳 **Multi-stage Dockerfile** — Imagem otimizada com usuário non-root
- 🛡️ **Rate Limiting** — Proteção contra brute-force em login (5/min) e registro (3/min)
- 🔑 **Validação de Senha Forte** — Exige maiúscula + dígito + mínimo 8 caracteres
- 🔄 **Auto Rehash** — Atualiza hashes automaticamente quando parâmetros do Argon2 mudam
- ✅ **25 Testes Automatizados** — Cobertura de todos os fluxos críticos + admin + validação

---

## 📂 Estrutura do Projeto

```
auth/
├── src/
│   ├── main.py                    # App FastAPI, CORS, exception handlers
│   ├── api/routes/
│   │   ├── auth.py                # POST register, login, refresh, logout
│   │   └── users.py               # GET/PATCH /me, PUT /password, admin routes
│   ├── core/
│   │   ├── config.py              # Settings (env vars, JWT, CORS)
│   │   ├── security.py            # Argon2, JWT encode/decode
│   │   └── dependencies.py        # get_current_user, require_admin
│   ├── services/
│   │   ├── auth_service.py        # Lógica: register, login, refresh, logout
│   │   └── user_service.py        # Lógica: CRUD de usuários, troca de senha
│   ├── models/
│   │   └── models.py              # User, RefreshToken, PasswordResetToken, ActivityLog
│   ├── schemas/
│   │   └── schemas.py             # Request/Response Pydantic models
│   └── db/
│       └── session.py             # Async engine + sessionmaker
├── tests/
│   ├── conftest.py                # Fixtures compartilhadas
│   ├── helpers.py                 # Utilitários de teste (auth_header)
│   └── test_auth.py               # 25 testes automatizados
├── alembic/                       # Database migrations
├── docker-compose.yml             # API + PostgreSQL
├── Dockerfile                     # Multi-stage, non-root
└── pyproject.toml                 # Dependências e config
```

---

## 🚀 Endpoints da API

### 🔐 Autenticação (`/api/v1/auth`)
| Método | Rota | Descrição | Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/register` | Registrar novo usuário | ❌ |
| `POST` | `/login` | Login com credenciais | ❌ |
| `POST` | `/refresh` | Renovar tokens (rotation) | ❌ |
| `POST` | `/logout` | Revogar refresh token | ❌ |

> ⚠️ `/login` limitado a **5 req/min** por IP · `/register` limitado a **3 req/min** por IP

### 👤 Usuários (`/api/v1/users`)
| Método | Rota | Descrição | Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/me` | Perfil do usuário atual | 🔒 Bearer |
| `PATCH` | `/me` | Atualizar email | 🔒 Bearer |
| `PUT` | `/me/password` | Trocar senha | 🔒 Bearer |
| `GET` | `/` | Listar usuários | 🔒 Admin |
| `PUT` | `/{id}/status` | Ativar/desativar usuário | 🔒 Admin |

### 🔧 Sistema
| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check |
| `GET` | `/` | Info da API |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

---

## ⚡ Quickstart

### Com Docker (recomendado)
```bash
# Subir tudo
docker compose up -d

# API disponível em http://localhost:8000/docs
```

### Local (dev)
```bash
# Instalar dependências
pip install -e ".[dev]"

# Configurar .env
cp .env.example .env

# Rodar testes
pytest -v

# Iniciar servidor
fastapi dev src/main.py
```

### Exemplo de uso
```bash
# 1. Registrar
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'

# 3. Acessar perfil (com token)
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"

# 4. Trocar senha
curl -X PUT http://localhost:8000/api/v1/users/me/password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"current_password": "securepass123", "new_password": "newpass456"}'
```

---

## 📈 Changelog

### v0.2.0 (atual)
- ✅ **Service Layer** — Lógica extraída das rotas para `services/`
- ✅ **CORS Middleware** — Frontend pode se conectar ao backend
- ✅ **Refresh token retornado** — Fix: agora o `TokenResponse` inclui o refresh token
- ✅ **RBAC** — `require_admin` dependency para rotas admin
- ✅ **Token Reuse Detection** — Proteção contra reutilização de tokens revogados
- ✅ **JWT `jti`** — Cada token é único (UUID)
- ✅ **Rotas de usuário** — `PATCH /me`, `PUT /me/password`, admin list/toggle
- ✅ **18 testes** — Cobertura de register, login, refresh, logout, /me, password change
- ✅ **Campos padronizados** — Nomes em inglês (`is_revoked`, `expires_at`, `created_at`)
- ✅ **SECRET_KEY forte** — 256-bit gerada com `secrets.token_hex(32)`
- ✅ **Multi-stage Dockerfile** — Imagem menor, usuário non-root
- ✅ **Docker Compose** — Networks, restart policies

### v0.2.1 (atual)
- ✅ **Rate Limiting** — slowapi com 5/min login, 3/min register
- ✅ **Validação de senha forte** — Maiúscula + dígito obrigatórios
- ✅ **Auto Rehash** — `needs_rehash()` chamada a cada login
- ✅ **25 testes** — +7 testes (admin CRUD, acesso negado, validação de senha)
- ✅ **ActivityLog nullable** — FK fix para tentativas falhadas
- ✅ **model_validate()** — DRY nas rotas de usuário
- ✅ **UUID nos path params** — Validação automática pelo FastAPI
- ✅ **CORS strip** — Tratamento de espaços nas origins
- ✅ **Dockerfile fix** — Build stage com código-fonte

### v0.1.0
- Estrutura inicial com register, login, refresh, logout
- Argon2 + JWT (HS256)
- PostgreSQL + Alembic
- 8 testes básicos

---

<p align="center">
  <i>Desenvolvido com foco em segurança, escalabilidade e profissionalismo.</i>
</p>
