#!/bin/bash
# 🚀 Quick Start - Sistema de Recomendação com TMDB + MovieLens

set -e

echo "============================================================"
echo "🎬 Sistema de Recomendação de Filmes"
echo "   TMDB + MovieLens + Algoritmos Inteligentes"
echo "============================================================"
echo ""

# Verificar se está no diretório correto
if [ ! -f "README.md" ]; then
    echo "❌ Execute este script do diretório raiz do projeto"
    exit 1
fi

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para perguntar
ask() {
    echo -e "${YELLOW}$1${NC}"
    read -p "Escolha: " choice
    echo "$choice"
}

# Passo 1: Ambiente Python
echo -e "${BLUE}📦 PASSO 1: Configurando ambiente Python${NC}"
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
fi

echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "Instalando dependências..."
pip install -r backend/requirements.txt

echo -e "${GREEN}✅ Ambiente Python configurado${NC}\n"

# Passo 2: Configurar .env
echo -e "${BLUE}📝 PASSO 2: Configurando credenciais${NC}"
if [ ! -f "backend/.env" ]; then
    cp backend/.env backend/.env.backup 2>/dev/null || true
    echo "Arquivo .env já existe!"
else
    echo "✅ Credenciais TMDB configuradas"
fi
echo ""

# Passo 3: Dados
echo -e "${BLUE}🎬 PASSO 3: Escolha o dataset${NC}"
echo "1. Teste rápido (5 filmes, 30 segundos)"
echo "2. MovieLens pequeno (100 filmes, 5 minutos)"
echo "3. MovieLens completo (9.000 filmes, 3-4 horas)"
echo "4. Usar dados mock (100 filmes em português, 0 segundos)"
echo ""

choice=$(ask "Qual opção?")

cd backend

case $choice in
    1)
        echo -e "${BLUE}🧪 Executando teste rápido...${NC}"
        python test_tmdb.py
        ;;
    2)
        echo -e "${BLUE}📥 Baixando e enriquecendo 100 filmes...${NC}"
        echo "2" | python setup_data.py
        ;;
    3)
        echo -e "${BLUE}📥 Baixando e enriquecendo dataset completo...${NC}"
        echo "Isso pode levar algumas horas!"
        echo "1" | python setup_data.py
        ;;
    4)
        echo -e "${GREEN}✅ Usando dados mock (já incluídos)${NC}"
        ;;
    *)
        echo -e "${YELLOW}⚠️  Opção inválida, usando dados mock${NC}"
        ;;
esac

cd ..

echo ""
echo -e "${GREEN}✅ Dados prontos!${NC}\n"

# Passo 4: Frontend
echo -e "${BLUE}⚛️  PASSO 4: Configurando frontend${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Instalando dependências do frontend..."
    npm install
else
    echo "✅ Dependências já instaladas"
fi

cd ..

echo -e "${GREEN}✅ Frontend configurado${NC}\n"

# Passo 5: Iniciar servidores
echo "============================================================"
echo -e "${GREEN}🎉 TUDO PRONTO!${NC}"
echo "============================================================"
echo ""
echo "Para iniciar o sistema:"
echo ""
echo "  Terminal 1 (Backend):"
echo "  $ cd backend"
echo "  $ source ../.venv/bin/activate"
echo "  $ uvicorn app.main:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "  $ cd frontend"
echo "  $ npm run dev"
echo ""
echo "  Depois acesse: http://localhost:5173"
echo ""

# Perguntar se quer iniciar automaticamente
echo ""
choice=$(ask "Deseja iniciar os servidores agora? (s/n)")

if [ "$choice" = "s" ] || [ "$choice" = "S" ]; then
    echo ""
    echo "🚀 Iniciando servidores..."
    echo ""
    
    # Iniciar backend
    cd backend
    source ../.venv/bin/activate
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    sleep 2
    
    # Iniciar frontend
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "============================================================"
    echo "✅ Servidores iniciados!"
    echo "============================================================"
    echo ""
    echo "Backend:  http://localhost:8000"
    echo "Frontend: http://localhost:5173"
    echo ""
    echo "📝 Para parar os servidores:"
    echo "   kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "Pressione Ctrl+C para parar todos os servidores"
    
    # Aguardar
    wait
else
    echo ""
    echo "👋 Até logo! Execute os comandos acima quando quiser iniciar."
fi
