# 🎬 Movie Recommender

Sistema de recomendação de filmes inteligente utilizando dados do TMDB (The Movie Database) e MovieLens, com interface web moderna e API REST.

## 📋 Sobre o Projeto

O Movie Recommender é uma aplicação full-stack que oferece recomendações personalizadas de filmes baseadas em análise de conteúdo e preferências do usuário. O sistema utiliza algoritmos de machine learning para sugerir filmes similares aos que o usuário gostou.

### Principais Funcionalidades

- 🎯 **Recomendações Personalizadas**: Sistema baseado em conteúdo que analisa características dos filmes
- 👤 **Autenticação de Usuários**: Sistema completo de registro e login
- ⭐ **Feedback de Filmes**: Avaliações com likes/dislikes e ratings
- 📊 **Dados Enriquecidos**: Informações detalhadas dos filmes via API do TMDB
- 🎨 **Interface Moderna**: UI responsiva construída com React e Tailwind CSS
- 🚀 **API REST**: Backend robusto com FastAPI

## 🏗️ Arquitetura

```
movie-recommender/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Aplicação principal
│   │   ├── recommender.py  # Algoritmo de recomendação
│   │   ├── auth.py         # Sistema de autenticação
│   │   ├── database.py     # Gerenciamento de banco de dados
│   │   ├── models.py       # Modelos de dados
│   │   ├── data.py         # Processamento de dados
│   │   └── tmdb_client.py  # Cliente da API TMDB
│   ├── data/               # Dados dos filmes e cache
│   └── requirements.txt    # Dependências Python
│
└── frontend/               # Aplicação React
    ├── src/
    │   ├── App.tsx         # Componente principal
    │   ├── api.ts          # Cliente da API
    │   └── components/     # Componentes React
    ├── package.json
    └── vite.config.ts
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Node.js 16+ e npm
- API Key do TMDB ([obtenha aqui](https://www.themoviedb.org/settings/api))

### Configuração Rápida

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

# Configurar variável de ambiente (opcional)
export TMDB_API_KEY="sua_chave_api_aqui"

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

## 🔧 API Endpoints

### Autenticação

- `POST /register` - Registrar novo usuário
- `POST /login` - Fazer login
- `GET /me` - Obter dados do usuário atual

### Filmes

- `GET /movies` - Listar todos os filmes
- `GET /movies/{movie_id}` - Obter detalhes de um filme

### Recomendações

- `GET /recommendations?k=10` - Obter recomendações personalizadas
  - `k`: número de recomendações (padrão: 10)

### Feedback

- `POST /feedback` - Registrar like/dislike

  ```json
  {
    "movie_id": 1,
    "action": "like" // ou "dislike"
  }
  ```

- `POST /rate` - Avaliar filme com nota
  ```json
  {
    "movie_id": 1,
    "rating": 4.5
  }
  ```

## 🧪 Testes

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

## 📊 Dados

O projeto utiliza:

- **MovieLens Dataset**: Base de dados com milhares de filmes e avaliações
- **TMDB API**: Metadados enriquecidos, posters, sinopses e informações detalhadas
- **Cache Local**: Sistema de cache para otimizar requisições à API do TMDB

### Scripts de Dados

- `setup_data.py` - Configurar dataset inicial
- `collect_from_tmdb.py` - Coletar dados da API do TMDB
- `enrich_financial_data.py` - Enriquecer dados com informações financeiras

## 🤖 Algoritmo de Recomendação

O sistema utiliza **Content-Based Filtering**, analisando:

- 🎭 Gêneros dos filmes
- 📝 Palavras-chave e tags
- 👥 Diretores e atores
- 📅 Ano de lançamento
- ⭐ Avaliações médias

O algoritmo:

1. Extrai features TF-IDF dos metadados
2. Calcula similaridade de cosseno entre filmes
3. Pondera baseado no feedback do usuário
4. Retorna top-K recomendações com explicações

## 🛠️ Tecnologias Utilizadas

### Backend

- **FastAPI** - Framework web moderno e rápido
- **Scikit-learn** - Algoritmos de machine learning
- **Pandas** - Manipulação de dados
- **HTTPX** - Cliente HTTP assíncrono

### Frontend

- **React** - Biblioteca UI
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Framework CSS utility-first
- **Axios** - Cliente HTTP

## 📝 Configuração de Desenvolvimento

### Variables de Ambiente

Backend (`backend/.env`):

```env
TMDB_API_KEY=sua_chave_aqui
DATABASE_URL=sqlite:///./data/app.db
SECRET_KEY=chave_secreta_para_jwt
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

Desenvolvido como projeto de sistema de recomendação de filmes.

## 🙏 Agradecimentos

- [TMDB](https://www.themoviedb.org/) pelos dados de filmes
- [MovieLens](https://movielens.org/) pelo dataset
- Comunidade open source

---

⭐ Se este projeto foi útil, considere dar uma estrela no repositório!
