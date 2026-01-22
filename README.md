# 🎬 Movie Recommender

Sistema de recomendação de filmes inteligente utilizando dados do TMDB (The Movie Database) e MovieLens, com interface web moderna e API REST.

## � Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Instalação e Configuração](#-instalação-e-configuração)
- [API Reference](#-api-reference)
- [Modelos de Dados](#-modelos-de-dados)
- [Sistema de Recomendação](#-sistema-de-recomendação)
- [Autenticação](#-autenticação)
- [Scripts Utilitários](#-scripts-utilitários)
- [Testes](#-testes)
- [Tecnologias](#-tecnologias)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Contribuindo](#-contribuindo)

## 📋 Sobre o Projeto

O Movie Recommender é uma aplicação full-stack que oferece recomendações personalizadas de filmes baseadas em análise de conteúdo e preferências do usuário. O sistema utiliza algoritmos de machine learning para sugerir filmes similares aos que o usuário gostou.

### Principais Funcionalidades

- 🎯 **Recomendações Personalizadas**: Sistema baseado em conteúdo que analisa características dos filmes
- 👤 **Autenticação de Usuários**: Sistema completo de registro e login com bcrypt
- ⭐ **Feedback de Filmes**: Avaliações com likes/dislikes e ratings (1-5 estrelas)
- 📊 **Dados Enriquecidos**: Informações detalhadas de 5000+ filmes via API do TMDB
- 🎨 **Interface Moderna**: UI responsiva construída com React e Tailwind CSS
- 🚀 **API REST**: Backend robusto com FastAPI e validação automática
- 🔍 **Busca Avançada**: Filtros por gênero, ano, popularidade e keywords
- 🤖 **Machine Learning**: TF-IDF e similaridade de cosseno para recomendações
- 💾 **Cache Inteligente**: Sistema de cache local para otimizar performance

## 🏗️ Arquitetura

### Estrutura do Projeto

```
movie-recommender/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py              # FastAPI app + endpoints
│   │   ├── recommender.py       # Algoritmo de recomendação ML
│   │   ├── auth.py              # Sistema de tokens
│   │   ├── database.py          # DB em memória (usuários)
│   │   ├── models.py            # Modelos Pydantic (schemas)
│   │   ├── data.py              # Processamento de dataset
│   │   ├── tmdb_client.py       # Cliente API TMDB
│   │   ├── data_enricher.py     # Enriquecimento de dados
│   │   ├── movielens_loader.py  # Carregamento MovieLens
│   │   └── setup_data.py        # Inicialização do dataset
│   ├── data/
│   │   ├── movies_enriched.json # Dataset principal (5000+ filmes)
│   │   ├── enriched_movies.json # Backup enriquecido
│   │   ├── cache/               # Cache de chamadas TMDB
│   │   └── movielens/           # Dataset MovieLens original
│   ├── collect_from_tmdb.py     # Script coleta dados TMDB
│   ├── enrich_financial_data.py # Script enriquece dados financeiros
│   ├── test_tmdb.py             # Teste de conexão TMDB
│   ├── test_recommender.py      # Teste do recomendador
│   ├── setup_data.py            # Setup inicial do dataset
│   └── requirements.txt         # Dependências Python
│
├── frontend/                # Aplicação React
│   ├── src/
│   │   ├── App.tsx              # Componente principal
│   │   ├── api.ts               # Cliente da API
│   │   ├── AuthModal.tsx        # Modal de autenticação
│   │   ├── components/          # Componentes React
│   │   └── hooks/               # Custom hooks
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── quickstart.sh            # Setup automático completo
├── setup.sh                 # Script de configuração
└── validate.sh              # Validação do sistema
```

### Stack Tecnológico

**Backend:**

- FastAPI (framework web assíncrono)
- Scikit-learn (TF-IDF, similaridade de cosseno)
- Pandas & NumPy (manipulação de dados)
- HTTPX (cliente HTTP assíncrono)
- bcrypt (hash de senhas)
- Pydantic (validação de dados)

**Frontend:**

- React 18 (biblioteca UI)
- TypeScript (type safety)
- Vite (build tool)
- Tailwind CSS (estilização)
- Axios (cliente HTTP)

**Dados:**

- TMDB API (metadados de filmes)
- MovieLens Dataset (avaliações de usuários)

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Node.js 16+ e npm
- API Key do TMDB ([obtenha aqui](https://www.themoviedb.org/settings/api))

### Configuração Rápida (Recomendado)

O projeto inclui scripts automatizados para facilitar a configuração:

```bash
# Dar permissão de execução aos scripts
chmod +x quickstart.sh setup.sh validate.sh

# Executar configuração completa
./quickstart.sh
```

Este script irá:

1. Configurar o ambiente Python
2. Instalar dependências do backend
3. Configurar o ambiente Node.js
4. Instalar dependências do frontend
5. Iniciar ambos os servidores

### Configuração Manual

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# (Opcional) Configurar API Key do TMDB
export TMDB_API_KEY="sua_chave_api_aqui"

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

O servidor estará rodando em: `http://localhost:8000`

**Documentação Interativa:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

### Variáveis de Ambiente

**Backend** (`backend/.env`):

```env
TMDB_API_KEY=sua_chave_aqui
TOKEN_EXPIRY_HOURS=168  # 7 dias
```

**Frontend** (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

### Proxy do Vite

O frontend já está configurado para fazer proxy das requisições `/api/*` para o backend em `http://localhost:8000/*`.

## 🔧 API Reference

### Autenticação

#### `POST /register`

Registra novo usuário no sistema.

**Request Body:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "senha_segura"
}
```

**Response (201):**

```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-01-21T10:30:00"
  },
  "token": "eyJhbGc..."
}
```

#### `POST /login`

Autentica usuário existente.

**Request Body:**

```json
{
  "username": "johndoe",
  "password": "senha_segura"
}
```

**Response (200):**

```json
{
  "user": {...},
  "token": "eyJhbGc..."
}
```

#### `GET /me`

Retorna dados do usuário autenticado.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "liked_movies": [1, 5, 10],
  "disliked_movies": [2, 7],
  "ratings": { "3": 5, "8": 4 }
}
```

### Filmes

#### `GET /movies`

Lista filmes com filtros avançados.

**Query Parameters:**

- `genre` (string): Filtrar por gênero (ex: "Action", "Drama")
- `min_rating` (float): Avaliação mínima TMDB (0-10)
- `min_popularity` (float): Popularidade mínima
- `year_from` (int): Ano inicial
- `year_to` (int): Ano final
- `keyword` (string): Busca no título, sinopse ou keywords

**Exemplo:**

```bash
GET /movies?genre=Action&min_rating=7.0&year_from=2020
```

**Response (200):**

```json
[
  {
    "id": 1,
    "title": "The Dark Knight",
    "year": 2008,
    "genres": ["Action", "Crime", "Drama"],
    "director": "Christopher Nolan",
    "description": "Batman must accept...",
    "tmdb_id": 155,
    "vote_average": 8.5,
    "popularity": 123.45,
    "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    "keywords": ["dc comics", "superhero", "joker"],
    "cast": ["Christian Bale", "Heath Ledger"],
    "runtime": 152,
    "budget": 185000000,
    "revenue": 1004558444
  }
]
```

#### `GET /movies/{movie_id}`

Retorna detalhes completos de um filme específico.

**Response (200):** Objeto `Movie` completo

#### `GET /movies/{movie_id}/similar`

Retorna filmes similares baseados em gêneros, keywords e diretor.

**Query Parameters:**

- `limit` (int): Número de filmes (padrão: 5)

**Response (200):** Array de objetos `Movie`

### Recomendações

#### `GET /recommendations`

**🔒 Requer Autenticação**

Retorna recomendações personalizadas baseadas no histórico do usuário.

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `k` (int): Número de recomendações (padrão: 10, máx: 50)

**Response (200):**

```json
{
  "user_id": 1,
  "recommendations": [
    {
      "movie": {
        "id": 42,
        "title": "Inception",
        "year": 2010,
        ...
      },
      "score": 0.8745,
      "explanation": "Similar to 'Interstellar' (liked) - Shared genres: Sci-Fi, Thriller. Same director: Christopher Nolan."
    }
  ],
  "based_on": {
    "liked_count": 5,
    "disliked_count": 2,
    "rated_count": 3
  }
}
```

### Feedback

#### `POST /feedback`

**🔒 Requer Autenticação**

Registra like ou dislike em um filme.

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "movie_id": 42,
  "action": "like" // ou "dislike"
}
```

**Response (200):**

```json
{
  "message": "Feedback registrado com sucesso",
  "movie_id": 42,
  "action": "like"
}
```

#### `POST /rate`

**🔒 Requer Autenticação**

Avalia um filme com nota de 1 a 5 estrelas.

**Request Body:**

```json
{
  "movie_id": 42,
  "rating": 5
}
```

**Response (200):**

```json
{
  "message": "Avaliação registrada com sucesso",
  "movie_id": 42,
  "rating": 5
}
```

### Utilitários

#### `GET /health`

Verifica status da API.

**Response (200):**

```json
{
  "ok": true,
  "users": 42,
  "movies": 5234
}
```

## 📊 Modelos de Dados

### Movie

```python
{
  "id": int,                          # ID único do filme
  "title": str,                       # Título
  "year": int,                        # Ano de lançamento
  "genres": List[str],                # Gêneros
  "director": str,                    # Diretor principal
  "description": str,                 # Descrição/sinopse

  # IDs Externos
  "tmdb_id": int | None,              # ID no TMDB
  "imdb_id": str | None,              # ID no IMDb

  # Metadados TMDB
  "original_title": str | None,       # Título original
  "original_language": str | None,    # Idioma original
  "overview": str | None,             # Sinopse completa
  "tagline": str | None,              # Frase de efeito
  "runtime": int | None,              # Duração (minutos)
  "release_date": str | None,         # Data de lançamento

  # Avaliações
  "vote_average": float | None,       # Nota média (0-10)
  "vote_count": int | None,           # Número de votos
  "popularity": float | None,         # Score de popularidade
  "rating_stats": {                   # Stats do MovieLens
    "average": float | None,
    "count": int | None,
    "min": float | None,
    "max": float | None
  },

  # Conteúdo Rico
  "keywords": List[str] | None,       # Keywords/tags do TMDB
  "cast": List[str] | None,           # Elenco principal
  "production_companies": List[str],  # Produtoras
  "production_countries": List[str],  # Países de produção

  # Imagens
  "poster_path": str | None,          # Caminho do poster
  "backdrop_path": str | None,        # Imagem de fundo

  # Financeiro
  "budget": int | None,               # Orçamento (USD)
  "revenue": int | None,              # Receita (USD)

  # Outros
  "adult": bool | None,               # Conteúdo adulto
  "belongs_to_collection": {...},     # Franquia/coleção
  "spoken_languages": [...]           # Idiomas falados
}
```

### User (Response)

```python
{
  "id": int,
  "username": str,
  "email": str,
  "created_at": str,                  # ISO 8601 datetime
  "liked_movies": List[int],          # IDs dos filmes curtidos
  "disliked_movies": List[int],       # IDs dos filmes não curtidos
  "ratings": Dict[int, int]           # {movie_id: rating}
}
```

### Backend

```bash
cd backend
source .venv/bin/activate

# Testar conexão com TMDB
python test_tmdb.py

# Testar sistema de recomendação
python test_recommender.py
```

### Validação Completa

```bash
./validate.sh
```

## 🤖 Sistema de Recomendação

### Algoritmo: Content-Based Filtering

O sistema utiliza análise de conteúdo baseada em **TF-IDF** (Term Frequency-Inverse Document Frequency) e **similaridade de cosseno**.

### Pipeline de Recomendação

1. **Feature Extraction**
   - Extrai características textuais de cada filme
   - Combina múltiplos atributos com pesos estratégicos

2. **Vetorização TF-IDF**
   - Converte texto em vetores numéricos
   - Pondera importância relativa de cada termo

3. **Cálculo de Similaridade**
   - Usa similaridade de cosseno entre vetores
   - Identifica filmes com características similares

4. **Personalização**
   - Considera histórico do usuário (likes, dislikes, ratings)
   - Exclui filmes já avaliados
   - Gera explicações das recomendações

### Features Utilizadas (com pesos)

| Feature               | Peso | Descrição                  |
| --------------------- | ---- | -------------------------- |
| **Keywords TMDB**     | 6x   | Tags precisas do conteúdo  |
| **Gêneros**           | 5x   | Categorias principais      |
| **Diretor**           | 3x   | Estilo único do diretor    |
| **Certificação**      | 2x   | Público-alvo (PG, R, etc.) |
| **Elenco**            | 2x   | Top 5 atores principais    |
| **Sinopse**           | 1x   | Primeiras 150 palavras     |
| **Empresas**          | 1x   | Top 3 produtoras           |
| **Década**            | 1x   | Contexto temporal          |
| **Idioma**            | 1x   | Tipo de produção           |
| **Países**            | 1x   | Estilo regional            |
| **Popularidade Tier** | 1x   | Alcance do filme           |
| **Tagline**           | 1x   | Frase de efeito            |

### Exemplo de Feature Extraction

```python
# Input: Filme "Inception" (2010)
movie_text = """
generos:scifi thriller scifi thriller scifi thriller scifi thriller scifi thriller
keywords:dream heist subconscious mindbending dream heist subconscious mindbending...
diretor:christopher nolan christopher nolan christopher nolan
elenco:leonardo dicaprio joseph gordonlevitt
certificacao:pg13 pg13
decada:2010s
idioma:en
paises:us uk
...
"""
# Output: Vetor TF-IDF de dimensão ~1000+
```

### Geração de Explicações

As recomendações incluem explicações detalhadas:

```
"Similar to 'Interstellar' (liked) - Shared genres: Sci-Fi, Thriller.
Same director: Christopher Nolan. Common keywords: space, time, science."
```

### Fallback: Cold Start

Para usuários novos (sem histórico), o sistema retorna:

- Filmes mais populares
- Melhor avaliados (vote_average)
- Diversidade de gêneros

## 🔐 Autenticação

### Sistema de Tokens

- **Geração**: Tokens seguros com `secrets.token_urlsafe(32)`
- **Armazenamento**: Em memória (dict) com timestamp de expiração
- **Expiração**: 7 dias (168 horas) por padrão
- **Validação**: Middleware que verifica token em cada requisição protegida

### Segurança de Senhas

- **Hash**: bcrypt com salt automático
- **Verificação**: Comparação segura com timing constante
- **Armazenamento**: Apenas hash, nunca senha em texto plano

### Uso da Autenticação

```bash
# Todas as requisições protegidas requerem header:
Authorization: Bearer <token>

# Exemplo com curl:
curl -H "Authorization: Bearer abc123..." \
  http://localhost:8000/recommendations
```

### Endpoints Públicos

- `POST /register`
- `POST /login`
- `GET /health`
- `GET /movies` (listagem básica)
- `GET /movies/{id}`

### Endpoints Protegidos 🔒

- `GET /me`
- `GET /recommendations`
- `POST /feedback`
- `POST /rate`

## 🛠️ Scripts Utilitários

### `setup_data.py`

Inicializa o dataset combinando MovieLens e dados TMDB.

```bash
cd backend
python setup_data.py
```

### `collect_from_tmdb.py`

Coleta dados detalhados da API do TMDB para todos os filmes.

```bash
cd backend
python collect_from_tmdb.py
```

**Recursos:**

- Rate limiting automático (40 req/10s)
- Sistema de cache local
- Retry com backoff exponencial
- Barra de progresso

### `enrich_financial_data.py`

Enriquece dataset com dados financeiros (budget, revenue).

```bash
cd backend
python enrich_financial_data.py
```

### `test_tmdb.py`

Testa conexão e funcionalidades da API TMDB.

```bash
cd backend
python test_tmdb.py
```

### `test_recommender.py`

Testa o sistema de recomendação com casos simulados.

```bash
cd backend
python test_recommender.py
```

## 🧪 Testes

### Teste de Conexão TMDB

```bash
cd backend
source .venv/bin/activate
python test_tmdb.py
```

Verifica:

- ✅ API key válida
- ✅ Busca de filmes
- ✅ Detalhes completos
- ✅ Keywords e credits

### Teste do Recomendador

```bash
cd backend
source .venv/bin/activate
python test_recommender.py
```

Testa:

- ✅ Recomendações básicas
- ✅ Personalização com likes/dislikes
- ✅ Filmes similares
- ✅ Cold start (sem histórico)

### Teste da API (manual)

```bash
# 1. Iniciar servidor
cd backend
uvicorn app.main:app --reload --port 8000

# 2. Em outro terminal
# Testar health check
curl http://localhost:8000/health

# Registrar usuário
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123"}'

# Listar filmes
curl http://localhost:8000/movies?genre=Action&min_rating=7.0
```

### Validação Completa

```bash
./validate.sh
```

## 🔧 Tecnologias

### Core Backend

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web assíncrono de alta performance
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validação de dados e serialização
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI

### Machine Learning

- **[Scikit-learn](https://scikit-learn.org/)** - TF-IDF e similaridade de cosseno
- **[NumPy](https://numpy.org/)** - Operações numéricas e arrays
- **[Pandas](https://pandas.pydata.org/)** - Manipulação de dados

### HTTP & External APIs

- **[HTTPX](https://www.python-httpx.org/)** - Cliente HTTP assíncrono
- **[TMDB API](https://www.themoviedb.org/documentation/api)** - Metadados de filmes

### Segurança

- **[bcrypt](https://github.com/pyca/bcrypt/)** - Hashing de senhas
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Variáveis de ambiente

### Frontend

- **[React](https://react.dev/)** - Biblioteca UI
- **[TypeScript](https://www.typescriptlang.org/)** - Type safety
- **[Vite](https://vitejs.dev/)** - Build tool moderno
- **[Tailwind CSS](https://tailwindcss.com/)** - Framework CSS utility-first
- **[Axios](https://axios-http.com/)** - Cliente HTTP

### Utilities

- **[tqdm](https://tqdm.github.io/)** - Barras de progresso
- **[python-dateutil](https://dateutil.readthedocs.io/)** - Manipulação de datas

## 📈 Performance

### Otimizações Implementadas

- ✅ **Cache Local**: Reduz chamadas à API TMDB em ~90%
- ✅ **TF-IDF Pré-computado**: Vetores calculados na inicialização
- ✅ **Índices de Memória**: Lookup O(1) para filmes por ID
- ✅ **Lazy Loading**: Carregamento sob demanda de dados grandes

### Benchmarks

- **Inicialização**: ~2-3 segundos (5000+ filmes)
- **Recomendação**: ~50-100ms por requisição
- **Listagem**: ~10-20ms (sem filtros)
- **Busca com filtros**: ~30-50ms

## 🔍 Troubleshooting

### Erro: "TMDB_API_KEY not found"

```bash
# Definir variável de ambiente
export TMDB_API_KEY="sua_chave_aqui"

# Ou criar arquivo .env
echo "TMDB_API_KEY=sua_chave_aqui" > backend/.env
```

### Erro: "Module not found"

```bash
# Reinstalar dependências
cd backend
pip install -r requirements.txt

# Verificar ambiente virtual está ativo
which python  # Deve apontar para .venv/bin/python
```

### Performance lenta

```bash
# Verificar se cache existe
ls -la backend/data/cache/

# Reconstruir cache se necessário
cd backend
python collect_from_tmdb.py
```

### Erro 401 nas requisições protegidas

```bash
# Verificar formato do header
Authorization: Bearer <token>  # ✅ Correto
Authorization: <token>          # ❌ Errado
```

### Frontend não conecta ao backend

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar configuração de proxy no vite.config.ts
# Deve apontar para http://localhost:8000
```

## 📝 Configuração de Desenvolvimento

### Variáveis de Ambiente

Backend (`backend/.env`):

```env
TMDB_API_KEY=sua_chave_aqui
TOKEN_EXPIRY_HOURS=168  # 7 dias
```

Frontend (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

### Proxy do Vite

O frontend já está configurado para fazer proxy das requisições `/api/*` para o backend em `http://localhost:8000/*`.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 👥 Autores

John Lenes Silva

## 🙏 Agradecimentos

- [TMDB](https://www.themoviedb.org/) pelos dados de filmes
- [MovieLens](https://movielens.org/) pelo dataset
- Comunidade open source

---

⭐ Se este projeto foi útil, considere dar uma estrela no repositório!
