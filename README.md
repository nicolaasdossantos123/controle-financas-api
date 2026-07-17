# API Finanças

## Sobre

API REST desenvolvida com FastAPI para gerenciamento de finanças pessoais.

A aplicação permite que cada usuário possua sua própria conta, realize autenticação por JWT e gerencie suas categorias e transações de forma segura. Todas as operações protegidas verificam a identidade do usuário através do token de autenticação, garantindo que cada usuário acesse apenas seus próprios dados.

---

## Funcionalidades

- Cadastro de usuários
- Login com autenticação JWT
- Criptografia de senhas utilizando bcrypt
- CRUD completo de categorias
- CRUD completo de transações
- Relacionamento entre categorias e transações
- Proteção das rotas privadas
- Validação de propriedade dos recursos
- Filtros opcionais para consulta de transações

---

## Tecnologias

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL
- python-jose (JWT)
- bcrypt
- Uvicorn

---

## Estrutura do projeto

```
projeto/
│
├── database.py
├── main.py
├── routers.py
├── schemas.py
├── requirements.txt
├── .env
└── README.md
```

---

## Instalação

Clone o repositório

```bash
git clone <url-do-repositorio>
```

Entre na pasta

```bash
cd api-financas
```

Crie um ambiente virtual

```bash
python -m venv venv
```

Ative o ambiente

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

Instale as dependências

```bash
pip install -r requirements.txt
```

---

## Configuração do .env

Crie um arquivo `.env`

```
SECRET_KEY=sua_chave_secreta
```

---

## Executando o projeto

```bash
uvicorn main:app --reload
```

Documentação automática

```
http://127.0.0.1:8000/docs
```

---

## Endpoints

### Usuários

| Método | Endpoint | Descrição |
|---------|----------|-----------|
| POST | /usuarios | Criar usuário |

---

### Login

| Método | Endpoint | Descrição |
|---------|----------|-----------|
| POST | /login | Gerar token JWT |

---

### Categorias

| Método | Endpoint |
|---------|----------|
| POST | /categorias |
| GET | /categorias |
| GET | /categorias/{id} |
| PUT | /categorias/{id} |
| DELETE | /categorias/{id} |

---

### Transações

| Método | Endpoint |
|---------|----------|
| POST | /transacoes |
| GET | /transacoes |
| GET | /transacoes/{id} |
| PUT | /transacoes/{id} |
| DELETE | /transacoes/{id} |

---

## Exemplos de requisição

### Criar usuário

```json
POST /usuarios
```

```json
{
    "nome": "Nicolau",
    "email": "nicolau@email.com",
    "senha": "123456"
}
```

---

### Login

```json
POST /login
```

```json
{
    "email": "nicolau@email.com",
    "senha": "123456"
}
```

Resposta

```json
{
    "access_token": "...",
    "token_type": "bearer"
}
```

---

### Criar categoria

```json
POST /categorias
```

```json
{
    "nome": "Alimentação"
}
```

---

### Criar transação

```json
POST /transacoes
```

```json
{
    "descricao": "Mercado",
    "valor": 150.90,
    "tipo": "saida",
    "data": "2026-07-20",
    "categoria_id": 1
}
```

---

## Filtros disponíveis

A rota

```
GET /transacoes
```

aceita filtros opcionais.

Buscar por tipo

```
GET /transacoes?tipo=entrada
```

Buscar por categoria

```
GET /transacoes?categoria_id=1
```

Buscar por período

```
GET /transacoes?data_inicio=2026-07-01
```

```
GET /transacoes?data_fim=2026-07-31
```

Combinando filtros

```
GET /transacoes?tipo=saida&categoria_id=2
```

```
GET /transacoes?tipo=entrada&data_inicio=2026-07-01&data_fim=2026-07-31
```

---

## Melhorias futuras

- Paginação nas listagens
- Pesquisa por descrição
- Ordenação personalizada
- Dashboard financeiro
- Resumo mensal de receitas e despesas
- Upload de comprovantes
- Exclusão lógica (Soft Delete)
- Refresh Token para autenticação
- Testes automatizados
- Docker
- Deploy em nuvem
- CI/CD
- Documentação mais detalhada
