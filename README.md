# 🔐 Auth System PRO

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens" alt="JWT">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

### 🚀 O "Porteiro Digital" Inteligente
O **Auth System PRO** não é apenas um sistema de login; é um **Serviço Central de Autenticação** de nível empresarial. Projetado para ser a espinha dorsal de segurança de ecossistemas modernos, ele permite que aplicações Web, Mobile e SaaS deleguem a complexidade da gestão de identidade a um núcleo robusto e altamente seguro.

---

## 📋 Sumário
- [🎯 O Conceito](#-o-conceito)
- [🛠️ Stack Tecnológica](#️-stack-tecnológica)
- [🔥 Diferenciais Técnicos](#-diferenciais-técnicos)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [📈 Roadmap de Desenvolvimento](#-roadmap-de-desenvolvimento)

---

## 🎯 O Conceito
Imagine um serviço universal que qualquer aplicação pode interrogar:
> **Aplicação Client:** "Este usuário com este token é confiável?"  
> **Auth System:** "Sim, é o Usuário X e ele possui as permissões Y. Acesso garantido."

### Objetivos:
1. **Universalidade:** Integração transparente com qualquer plataforma.
2. **Escalability:** Controle de sessões otimizado para alta demanda.
3. **Professionalism:** Arquitetura limpa seguindo os melhores padrões da indústria.

---

## 🛠️ Stack Tecnológica
- **Backend:** FastAPI (Assíncrono, Alta Performance)
- **Segurança:** `Argon2` para hashing e `PyJWT` para tokens JWT.
- **Persistência:** PostgreSQL com versionamento via **Alembic**.
- **Cache & Performance:** Redis para rate limiting e blacklist seletiva de tokens.
- **Containerization:** Docker & Docker Compose para ambientes isolados.
- **Coding Standard:** Pytest (Testes), Ruff (Linter) e Mypy (Tipagem).

---

## 🔥 Diferenciais Técnicos (Production-Ready)
- 🛡️ **Segurança Avançada:** Refresh Tokens via **Cookies HttpOnly/Secure/SameSite=Strict** (Proteção contra XSS e CSRF).
- 🔄 **Rotação de Refresh Token:** Cada uso do refresh token emite um novo e invalida o anterior — token roubado é detectado automaticamente.
- 🚫 **Token Revocation:** Logout revoga o refresh token no banco; access token expira em 30min (sem blacklist desnecessária).
- 🏗️ **Arquitetura Modular:** Separação clara de responsabilidades (Service/Repository Pattern).
- ⚙️ **Tratamento de Erros:** Handler global para respostas padronizadas e seguras.
- 🐳 **Pronto para Cloud:** Configurações otimizadas para deploy em containers.

---

## 📂 Estrutura do Projeto
Para uma visão detalhada da arquitetura, explore nossa documentação técnica:

| Arquivo/Pasta | Descrição |
| :--- | :--- |
| [`planejamento/projeto.md`](./planejamento/projeto.md) | Visão geral e objetivos de negócio. |
| [`planejamento/estrutura.md`](./planejamento/estrutura.md) | Detalhes da arquitetura técnica e DB. |
| [`planejamento/fase.md`](./planejamento/fase.md) | Cronograma de implementação por etapas. |
| [`planejamento/prioridade.md`](./planejamento/prioridade.md) | Mapeamento de tarefas críticas. |

---

## 📈 Roadmap de Desenvolvimento
O projeto está estruturado em 4 fases fundamentais:
1. **Fase 1:** Alicerce (Ambiente e Base de Dados).
2. **Fase 2:** Core Security (Auth Logic e JWT).
3. **Fase 3:** Robustez (Refresh Tokens e Logout).
4. **Fase 4:** Performance & QA (Redis e Testes finais).

---

<p align="center">
  <i>Desenvolvido com foco em segurança, escalabilidade e profissionalismo.</i>
</p>
