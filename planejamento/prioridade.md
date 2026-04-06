# Gestão de Prioridades

## 🔴 Crítico (Obrigatório para o MVP)
- **Fase 0 - Infra:** Docker setup e estrutura de pastas.
- **Hash de Senha:** Argon2 (`argon2-cffi`) — nunca bcrypt, nunca texto claro.
- **JWT:** `PyJWT` — geração e validação de access tokens.
- **Refresh Token:** UUID opaco em Cookie HttpOnly/Secure/SameSite=Strict + rotação obrigatória.
- **Alembic:** Versionamento de banco desde o início.
- **Proteção de Rotas:** Middleware valida JWT + `is_active`.

## 🟢 Alta (Diferencial Production-Ready)
- **Rotação de Refresh Token:** Detecta reuso → revoga todas as sessões do usuário.
- **Logout correto:** Revoga refresh token no banco — sem blacklist de access token (custo não justifica com 30min de expiração).
- **Testes de Integração:** Pytest com PostgreSQL real — fluxo completo Register → Login → Refresh → Logout.
- **Reset de Senha:** Token de uso único, 15min, hash no banco, revoga sessões após uso.
- **Global Error Handler:** Respostas padronizadas para o frontend.
- **`role` no usuário:** Campo para autorização básica (admin, user).

## 🟡 Média (Qualidade e Resiliência)
- **Ruff & Mypy:** Linter e checagem de tipos estáticos.
- **GitHub Actions:** CI para testes automáticos.
- **Logs de Atividade:** Auditoria de acessos e tentativas falhas.
- **Rate Limiting:** Prevenção de ataques de força bruta.



## 🔵 Baixa (Refinamento)
- **Integração Social:** Google/GitHub Login (Opcional).
- **MFA:** Autenticação de dois fatores.
- **Dashboard de Admin:** Visualização de usuários e logs.
