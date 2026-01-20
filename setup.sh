#!/bin/bash

# Script de configuração do sistema de recomendação MovieLens + TMDB
# Execute: bash setup.sh

echo "========================================"
echo "🎬 Setup MovieLens + TMDB Recommender"
echo "========================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    echo "   Instale Python 3.8+ antes de continuar."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION encontrado${NC}"
echo ""

# Criar ambiente virtual
echo "📦 Configurando ambiente virtual..."
cd backend

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
else
    echo -e "${YELLOW}⚠️  Ambiente virtual já existe${NC}"
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
echo ""
echo "📥 Instalando dependências..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependências instaladas com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências${NC}"
    exit 1
fi

# Configurar .env
echo ""
echo "⚙️  Configurando arquivo .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
    echo -e "${YELLOW}📝 ATENÇÃO: Configure TMDB_API_KEY no arquivo .env${NC}"
else
    echo -e "${YELLOW}⚠️  Arquivo .env já existe${NC}"
fi

# Criar diretórios
echo ""
echo "📁 Criando diretórios de dados..."
mkdir -p data/cache
mkdir -p data/movielens
echo -e "${GREEN}✅ Diretórios criados${NC}"

# Verificar chave TMDB
echo ""
echo "🔑 Verificando configuração TMDB..."
if grep -q "sua_chave_api_aqui" .env; then
    echo -e "${YELLOW}⚠️  TMDB_API_KEY não configurada!${NC}"
    echo ""
    echo "📝 Para obter sua chave API:"
    echo "   1. Acesse: https://www.themoviedb.org/settings/api"
    echo "   2. Crie uma conta gratuita (se não tiver)"
    echo "   3. Vá em 'Settings' → 'API'"
    echo "   4. Clique em 'Request an API Key'"
    echo "   5. Escolha 'Developer'"
    echo "   6. Preencha o formulário simples"
    echo "   7. Copie a 'API Key (v3 auth)'"
    echo "   8. Cole no arquivo backend/.env"
    echo ""
    read -p "Pressione ENTER quando tiver configurado a chave..."
else
    echo -e "${GREEN}✅ TMDB_API_KEY encontrada${NC}"
fi

# Baixar MovieLens (opcional)
echo ""
echo "📥 Dataset MovieLens"
echo "   O MovieLens fornece avaliações reais de usuários."
echo "   Datasets disponíveis:"
echo "   • ml-latest-small (~1MB) - 100k avaliações, 9k filmes"
echo "   • ml-latest (~300MB) - 27M avaliações, 58k filmes"
echo ""
read -p "Deseja baixar ml-latest-small automaticamente? (s/N): " DOWNLOAD

if [[ "$DOWNLOAD" =~ ^[Ss]$ ]]; then
    echo ""
    echo "📥 Baixando MovieLens ml-latest-small..."
    
    cd data/movielens
    
    if command -v wget &> /dev/null; then
        wget -q --show-progress https://files.grouplens.org/datasets/movielens/ml-latest-small.zip
    elif command -v curl &> /dev/null; then
        curl -# -L -O https://files.grouplens.org/datasets/movielens/ml-latest-small.zip
    else
        echo -e "${RED}❌ wget ou curl necessário para download${NC}"
        echo "   Baixe manualmente de: https://grouplens.org/datasets/movielens/"
        cd ../..
    fi
    
    if [ -f "ml-latest-small.zip" ]; then
        echo "📦 Extraindo arquivo..."
        unzip -q ml-latest-small.zip
        mv ml-latest-small/* .
        rm -rf ml-latest-small ml-latest-small.zip
        echo -e "${GREEN}✅ MovieLens baixado e extraído${NC}"
    fi
    
    cd ../..
else
    echo ""
    echo "💡 Você pode baixar manualmente depois:"
    echo "   1. Acesse: https://grouplens.org/datasets/movielens/"
    echo "   2. Baixe ml-latest-small.zip"
    echo "   3. Extraia em: backend/data/movielens/"
fi

# Executar setup de dados
echo ""
echo "🔄 Populando banco de dados..."
python -m app.setup_data

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dados configurados com sucesso!${NC}"
else
    echo -e "${YELLOW}⚠️  Erro ao configurar dados (usando fallback)${NC}"
fi

# Frontend
echo ""
echo "🎨 Configurando frontend..."
cd ../frontend

if command -v npm &> /dev/null; then
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Frontend configurado${NC}"
    else
        echo -e "${RED}❌ Erro ao configurar frontend${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  npm não encontrado, pule a configuração do frontend${NC}"
fi

cd ..

# Conclusão
echo ""
echo "========================================"
echo -e "${GREEN}✅ SETUP CONCLUÍDO!${NC}"
echo "========================================"
echo ""
echo "🚀 Para iniciar o sistema:"
echo ""
echo "Backend:"
echo "  cd backend"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "Frontend (outro terminal):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "📖 Acesse: http://localhost:5173"
echo ""
