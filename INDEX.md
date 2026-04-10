# Auth System PRO - Índice de Documentação

## Começar Aqui

1. **EXECUTIVO.md** - Resumo executivo (leia primeiro)
2. **SETUP_GUIDE.md** - Instruções de instalação e uso
3. **PROJECT_SUMMARY.md** - Visão técnica detalhada
4. **CHECKLIST.md** - Requisitos e funcionalidades validadas

---

## Estrutura do Código

```
src/
├── main.py                      # Aplicação FastAPI principal
├── api/
│   └── routes/
│       ├── auth.py              # Endpoints de autenticação
│       └── users.py             # Endpoints de usuários
├── core/
│   ├── config.py                # Configurações (Pydantic Settings)
│   ├── security.py              # Hash, JWT, validação
│   └── dependencies.py          # Dependency injection
├── models/
│   └── models.py                # SQLModel (User, RefreshToken, etc)
├── schemas/
│   └── schemas.py               # Pydantic validation
└── db/
    └── session.py               # Async database session
```

---

## Endpoints Rápidos

### Autenticação
```bash
# Registrar
POST /api/v1/auth/register
Body: {"email": "...", "password": "..."}

# Login
POST /api/v1/auth/login
Body: {"email": "...", "password": "..."}

# Renovar token
POST /api/v1/auth/refresh
Body: {"refresh_token": "..."}

# Logout
POST /api/v1/auth/logout
Body: {"refresh_token": "..."}
```

### Usuários
```bash
# Dados do usuário autenticado
GET /api/v1/users/me
Header: Authorization: Bearer <token>
```

---

## Instalação Rápida

### Docker (Recomendado)
```bash
cp .env.example .env
docker-compose up -d
# Acesse http://localhost:8000/docs
```

### Local
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
cp .env.example .env
fastapi run src/main.py
```

---

## Testes

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src

# Teste específico
pytest tests/test_auth.py::test_register_success -v
```

---

## Documentação Detalhada

### Para Desenvolvedores
- Leia: **PROJECT_SUMMARY.md**
- Arquitetura, modelos, segurança
- Exemplos de código

### Para DevOps
- Leia: **SETUP_GUIDE.md**
- Docker, deployment, variáveis de ambiente
- Health checks, logs

### Para QA/Testes
- Veja: **tests/test_auth.py**
- 8 testes unitários
- Exemplos de requisições

### Para Revisão
- Consulte: **CHECKLIST.md**
- Todos os requisitos validados
- Status de implementação

---

## Estrutura de Arquivos Criados

```
36 arquivos no total

CÓDIGO-FONTE:
  src/
  ├── main.py
  ├── api/routes/auth.py, users.py
  ├── core/config.py, security.py, dependencies.py
  ├── models/models.py
  ├── schemas/schemas.py
  └── db/session.py

TESTES:
  tests/test_auth.py

CONFIGURAÇÃO:
  pyproject.toml
  docker-compose.yml
  Dockerfile
  alembic.ini
  pytest.ini
  .env.example
  .gitignore
  requirements-dev.txt

DOCUMENTAÇÃO:
  EXECUTIVO.md
  SETUP_GUIDE.md
  PROJECT_SUMMARY.md
  CHECKLIST.md
  INDEX.md (este arquivo)

MIGRATIONS:
  alembic/env.py
  alembic/versions/ (vazio)

SCRIPTS:
  scripts/setup.sh
```

---

## Recursos de Segurança

✅ **Senhas**: Argon2 KDF
✅ **Tokens**: JWT HS256 com expiração
✅ **Refresh**: Revogação no banco
✅ **Deps**: Bearer + DB lookup
✅ **Email**: Validação + unique
✅ **Logs**: IP + User-Agent + Status

---

## Variáveis de Ambiente

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=sua-chave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Links Úteis

### Documentação Interativa
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Tecnologias
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [PyJWT](https://pyjwt.readthedocs.io/)
- [Argon2-cffi](https://argon2-cffi.readthedocs.io/)

---

## Próximos Passos

### Curto Prazo
1. Configurar .env com credenciais reais
2. Rodar docker-compose up -d
3. Acessar /docs para testar endpoints

### Médio Prazo
1. Adicionar email verification
2. Implementar password reset
3. Adicionar rate limiting

### Longo Prazo
1. OAuth2 integration
2. 2FA support
3. Admin dashboard

---

## FAQ

**P: Como mudo a porta?**
R: Edite `docker-compose.yml` ou use `fastapi run src/main.py --port 9000`

**P: Como adiciono um novo modelo?**
R: Crie em `src/models/models.py` e rode `alembic revision --autogenerate`

**P: Como configuro CORS?**
R: Edite `src/main.py` e adicione `app.add_middleware(CORSMiddleware, ...)`

**P: Posso usar SQLite?**
R: Sim, mude `DATABASE_URL` para `sqlite:///auth.db` em `.env`

---

## Suporte

Para mais informações, consulte:
- **SETUP_GUIDE.md** - Instalação detalhada
- **PROJECT_SUMMARY.md** - Arquitetura e design
- **tests/test_auth.py** - Exemplos de uso

---

**Versão**: 0.1.0
**Última atualização**: 2026-04-10
**Status**: Pronto para produção
