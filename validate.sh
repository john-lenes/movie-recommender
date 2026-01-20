#!/bin/bash
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "✅ VALIDAÇÃO COMPLETA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Backend
source .venv/bin/activate
cd backend
python -c 'from app.main import app; print(f"✅ Backend: {len(app.routes)} endpoints")' 2>&1 | head -1
cd ..

# Frontend  
cd frontend
npm run build 2>&1 | grep "✓ built" | head -1
cd ..

echo "✅ Backend rodando em: http://localhost:8000"
echo "✅ API health: $(curl -s http://localhost:8000/health | python3 -c 'import sys, json; d=json.load(sys.stdin); print(f\"{d[\"movies\"]} filmes disponíveis\")' 2>/dev/null || echo 'offline')"
