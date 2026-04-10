# Auth System PRO - Setup Guide

## Estrutura do Projeto

```
auth/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py      # Rotas de autenticação
│   │       └── users.py     # Rotas de usuários
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configurações com Pydantic
│   │   ├── security.py      # Hash, JWT, verificação
│   │   └── dependencies.py  # Injeção de dependências
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py        # Modelos SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py       # Schemas Pydantic
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py       # Engine e sessão async
│   └── main.py              # Aplicação FastAPI
├── tests/
│   ├── __init__.py
│   └── test_auth.py         # Testes unitários
├── alembic/
│   ├── env.py
│   └── versions/            # Migrações
├── scripts/
│   └── setup.sh             # Script de setup
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── pytest.ini
└── requirements-dev.txt
```

## Requisitos

- Python 3.12+
- PostgreSQL 16+ (ou use docker-compose)
- Redis (ou use docker-compose)

## Instalação Local

### 1. Clone ou configure o projeto

```bash
cd /Users/joao/projeto/repo\ projetos/auth
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### 4. Configure o arquivo .env

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
DATABASE_URL=postgresql+asyncpg://auth_user:auth_pass@localhost:5432/auth_db
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5. Crie o banco de dados (local)

```bash
createdb -U postgres auth_db
```

### 6. Execute as migrações

```bash
alembic upgrade head
```

### 7. Inicie o servidor

```bash
fastapi run src/main.py
```

O servidor estará disponível em `http://localhost:8000`

## Usando Docker Compose

### 1. Crie o arquivo .env

```bash
cp .env.example .env
```

### 2. Inicie os serviços

```bash
docker-compose up -d
```

Isto iniciará:
- API FastAPI na porta 8000
- PostgreSQL na porta 5432
- Redis na porta 6379

### 3. Crie as tabelas

```bash
docker-compose exec api alembic upgrade head
```

## Endpoints da API

### Autenticação

#### Registrar novo usuário
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Logout
```bash
POST /api/v1/auth/logout
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response:
{
  "message": "Logged out successfully"
}
```

### Usuários

#### Obter dados do usuário autenticado
```bash
GET /api/v1/users/me
Authorization: Bearer eyJ...

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-04-10T10:00:00Z"
}
```

## Testes

### Executar testes
```bash
pytest tests/
```

### Testes com cobertura
```bash
pytest tests/ --cov=src --cov-report=html
```

### Testes específicos
```bash
pytest tests/test_auth.py::test_register_success -v
```

## Recursos Implementados

### Autenticação
- ✓ Registro de usuários com validação de email
- ✓ Login com hash Argon2
- ✓ Tokens JWT com expiração configurável
- ✓ Refresh tokens com revogação
- ✓ Logout com revogação de tokens
- ✓ Dependência de usuário autenticado

### Banco de Dados
- ✓ Modelos SQLModel com async
- ✓ Relacionamentos (User, RefreshToken, PasswordResetToken, ActivityLog)
- ✓ Criação automática de tabelas
- ✓ Migrations com Alembic

### Segurança
- ✓ Hash de senhas com Argon2
- ✓ JWT com HS256
- ✓ Validação de tokens
- ✓ Proteção de dependência Bearer
- ✓ Log de atividades

### Validação
- ✓ Email válido (usando Pydantic EmailStr)
- ✓ Senha mínimo 8 caracteres
- ✓ Tratamento global de exceções
- ✓ Respostas JSON padronizadas

## Desenvolvimento

### Lint
```bash
ruff check src/ tests/
ruff format src/ tests/
```

### Type checking
```bash
mypy src/ --ignore-missing-imports
```

### Criar nova migração
```bash
alembic revision --autogenerate -m "Descrição da mudança"
```

## Variáveis de Ambiente

- `DATABASE_URL`: URL de conexão PostgreSQL
- `SECRET_KEY`: Chave secreta para JWT (mude em produção!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiração do access token (padrão: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Expiração do refresh token (padrão: 7)

## Documentação Interativa

Acesse `http://localhost:8000/docs` para a documentação Swagger interativa.

## Contribuições

1. Crie uma branch: `git checkout -b feature/sua-feature`
2. Commit as mudanças: `git commit -am 'Adiciona nova feature'`
3. Push para a branch: `git push origin feature/sua-feature`
4. Crie um Pull Request

## Licença

MIT
