# 🎬 Recomendador de Filmes - Sistema Inteligente

Sistema completo de recomendação de filmes em **Português Brasileiro** com integração **TMDB + MovieLens** e design moderno com **Tailwind CSS**.

## ✨ Funcionalidades

### 🎯 Dados Reais e Ricos

- **TMDB API**: Metadados completos (posters, sinopses, keywords, elenco)
- **MovieLens**: Avaliações reais de 100k+ usuários
- **Cache Inteligente**: Sistema de cache para performance
- **100 Filmes**: Selecionados entre os mais populares e bem avaliados

### Frontend (React + TypeScript + Vite + Tailwind CSS)
- 🎨 **Design Moderno**: Interface com Tailwind CSS e efeitos glass morphism
- 🌓 **Tema Claro/Escuro**: Alterne entre temas com persistência de preferência
- 📱 **Totalmente Responsivo**: Design mobile-first com 5 breakpoints (sm, md, lg, xl, 2xl)
- 🔍 **Busca Avançada**: Pesquise por título, diretor, gênero ou ano
- 🏷️ **Filtros Inteligentes**: Filtre por múltiplos gêneros e faixa de ano
- ⭐ **Sistema de Avaliações**: Avalie filmes com 1-5 estrelas
- 👍👎 **Like/Dislike**: Sistema rápido de feedback
- 📊 **Estatísticas**: Veja suas métricas de uso em tempo real
- 💾 **Persistência Local**: Suas preferências são salvas automaticamente
- 🎯 **Ordenação**: Ordene por ano, título ou avaliação
- ✨ **Animações Suaves**: Transições e animações com Tailwind
- 🎨 **Scrollbars Customizadas**: Estilo personalizado para melhor experiência

### Backend (FastAPI + Python + ML)
- 🤖 **Algoritmo Avançado**: TF-IDF com keywords, elenco e sinopses
- 📊 **TMDB Integration**: Metadados ricos de 58M+ filmes
- 🎬 **MovieLens Dataset**: Avaliações reais para melhor precisão
- 🎯 **Recomendações Explicáveis**: Entenda por que cada filme foi recomendado
- 🌈 **Diversidade**: Evita recomendações repetitivas de gêneros/diretores
- 📈 **Penalização de Dislikes**: Aprende com suas preferências negativas
- 💾 **Cache Inteligente**: Performance otimizada com cache de 7 dias
- 🔄 **API RESTful**: Endpoints bem documentados

## 🎨 Dataset Híbrido

### Fontes de Dados

1. **MovieLens** (Avaliações)
   - 100,000+ avaliações de usuários reais
   - 9,000+ filmes catalogados
   - Scores confiáveis e validados

2. **TMDB** (Metadados)
   - Posters e imagens em alta qualidade
   - Sinopses em português brasileiro
   - Keywords/tags (até 2.000 por filme)
   - Elenco completo e créditos
   - Classificação etária, duração, popularidade

### Dados Enriquecidos

Cada filme contém:
- ✅ Título original e traduzido
- ✅ 16 gêneros em pt-BR
- ✅ Diretor e top 5 atores
- ✅ Keywords para recomendação precisa
- ✅ Sinopse completa
- ✅ Poster e backdrop
- ✅ Avaliações reais do MovieLens
- ✅ Popularidade e votos do TMDB

## 🚀 Como Rodar

### Setup Rápido (Recomendado)

```bash
# 1. Clone o repositório
git clone <repo>
cd movie-recommender

# 2. Execute o setup automático
chmod +x setup.sh
./setup.sh

# O script irá:
# - Configurar ambiente Python
# - Instalar dependências
# - Solicitar chave API do TMDB
# - (Opcional) Baixar MovieLens
# - Popular banco de dados
```

### Setup Manual

#### 1) Configurar Backend

```bash
cd backend

# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Edite .env e adicione TMDB_API_KEY
# Obtenha em: https://www.themoviedb.org/settings/api

# Popular dados (TMDB + MovieLens)
python -m app.setup_data

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### 2) Configurar Frontend

```bash
cd frontend
npm install
npm run dev
```

**Acesse:** `http://localhost:5173`

---

## 🔑 Obtendo Chave TMDB API

1. Acesse: https://www.themoviedb.org/signup
2. Crie uma conta gratuita
3. Vá em Settings → API
4. Solicite uma API Key (escolha "Developer")
5. Copie a "API Key (v3 auth)"
6. Cole no arquivo `backend/.env`

**Ver guia completo:** [GUIA_TMDB_MOVIELENS.md](GUIA_TMDB_MOVIELENS.md)

---

## 📡 Endpoints da API

- `GET /health` - Status da API
- `GET /movies` - Lista todos os filmes
- `GET /state` - Estado atual (likes/dislikes)
- `POST /feedback` - Enviar like/dislike
  ```json
  { "movie_id": 1, "action": "like" | "dislike" }
  ```
- `GET /recommendations?k=10` - Obter recomendações personalizadas

## 🎯 Como Usar

1. **Explore o catálogo** de filmes na parte inferior
2. **Curta** (👍) ou **não curta** (👎) filmes que você conhece
3. **Avalie** filmes com estrelas (1-5) para melhor precisão
4. **Veja recomendações personalizadas** no topo da página
5. **Use filtros** para refinar sua busca por gênero e ano
6. **Alterne o tema** entre claro e escuro

## 🔬 Melhorias Implementadas

### Algoritmo de Recomendação
- ✅ Re-ranking com diversidade de gêneros e diretores
- ✅ Penalização forte de filmes não curtidos (90% redução)
- ✅ Boost para diversidade de diretores (+15%)
- ✅ Explicações detalhadas com emojis
- ✅ Fallback inteligente para novos usuários

### Interface do Usuário
- ✅ Sistema completo de temas (claro/escuro)
- ✅ Filtros por gênero com seleção múltipla
- ✅ Filtro de faixa de ano com sliders
- ✅ Ordenação por ano, título ou avaliação
- ✅ Sistema de avaliação por estrelas
- ✅ Estatísticas de uso (curtidas, avaliações, média)
- ✅ Persistência automática no localStorage
- ✅ Design moderno com gradientes e animações
- ✅ Estados vazios informativos

### Experiência do Usuário
- ✅ Totalmente traduzido para pt-BR
- ✅ Tooltips e mensagens descritivas
- ✅ Feedback visual imediato
- ✅ Layout responsivo mobile-first
- ✅ Carregamento otimizado
- ✅ Design moderno com Tailwind CSS
- ✅ Animações e transições suaves

## 🛠️ Tecnologias

**Backend:**
- FastAPI 0.115.0
- scikit-learn 1.5.2 (TF-IDF, Cosine Similarity)
- Pydantic 2.8.2
- Uvicorn 0.30.6
- python-dotenv 1.0.0
- requests 2.31.0

**Frontend:**
- React 18.3.1
- TypeScript 5.5.4
- Vite 5.4.2
- **Tailwind CSS 3.x** (Novo!)
- PostCSS + Autoprefixer

**APIs:**
- TMDB API (The Movie Database)
- MovieLens Dataset (ml-latest-small)

## 📚 Documentação

- [MIGRACAO_TAILWIND.md](./MIGRACAO_TAILWIND.md) - Detalhes da migração para Tailwind CSS
- [MELHORIAS.md](./MELHORIAS.md) - Melhorias técnicas implementadas
- [GUIA_DE_USO.md](./GUIA_DE_USO.md) - Guia completo para o usuário
- [INTEGRACAO_TMDB.md](./INTEGRACAO_TMDB.md) - Documentação da integração TMDB
- [RESUMO_MELHORIAS.md](./RESUMO_MELHORIAS.md) - Resumo executivo

## 📈 Próximos Passos

- [x] Integração com TMDB API
- [x] Integração com MovieLens
- [x] Design responsivo moderno
- [x] Migração para Tailwind CSS
- [ ] Persistência em banco de dados (SQLite/PostgreSQL)
- [ ] Sistema de usuários múltiplos
- [ ] Filtro colaborativo (usuários similares)
- [ ] Sistema de listas personalizadas
- [ ] Compartilhamento de recomendações
- [ ] PWA support
- [ ] Lazy loading de imagens

## 📝 Licença

Projeto educacional de sistema de recomendação.
