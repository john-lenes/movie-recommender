#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0

ok()   { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎬 Movie Recommender — Validação"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Ambiente Python ─────────────────────────
echo ""
echo "▶ Ambiente Python"

VENV_PYTHON=""
for P in "$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/backend/.venv/bin/python"; do
  [[ -x "$P" ]] && VENV_PYTHON="$P" && break
done

if [[ -z "$VENV_PYTHON" ]]; then
  fail "Virtualenv não encontrado — execute ./quickstart.sh ou ./setup.sh"
else
  ok "Virtualenv encontrado: $VENV_PYTHON"
fi

# ── 2. Dependências Python ─────────────────────
echo ""
echo "▶ Dependências Python"
if [[ -n "$VENV_PYTHON" ]]; then
  MISSING_DEPS=0
  for PKG in fastapi uvicorn pydantic bcrypt scikit_learn; do
    if "$VENV_PYTHON" -c "import $PKG" 2>/dev/null; then
      ok "Pacote $PKG instalado"
    else
      fail "Pacote $PKG não encontrado"
      MISSING_DEPS=1
    fi
  done
  [[ $MISSING_DEPS -eq 1 ]] && echo "     → Execute: pip install -r backend/requirements.txt"
fi

# ── 3. Backend — importação ────────────────────
echo ""
echo "▶ Backend (importação)"
if [[ -n "$VENV_PYTHON" ]]; then
  ENDPOINT_COUNT=$("$VENV_PYTHON" -c \
    "import sys; sys.path.insert(0,'$PROJECT_ROOT/backend'); from app.main import app; print(len(app.routes))" \
    2>&1)
  if echo "$ENDPOINT_COUNT" | grep -qE '^[0-9]+$'; then
    ok "Backend carregado — $ENDPOINT_COUNT endpoints registrados"
  else
    fail "Falha ao importar backend: $ENDPOINT_COUNT"
  fi
fi

# ── 4. Backend — arquivo .env ──────────────────
echo ""
echo "▶ Configuração"
if [[ -f "$PROJECT_ROOT/backend/.env" ]]; then
  ok ".env encontrado"
  if grep -q "TMDB_API_KEY=sua_chave" "$PROJECT_ROOT/backend/.env" 2>/dev/null; then
    fail "TMDB_API_KEY ainda é o valor padrão — configure com sua chave em backend/.env"
  else
    ok "TMDB_API_KEY parece configurada"
  fi
else
  fail "backend/.env não encontrado — crie a partir de backend/.env.example"
fi

# ── 5. Dataset ─────────────────────────────────
echo ""
echo "▶ Dataset"
DATA="$PROJECT_ROOT/backend/data/movies_enriched.json"
if [[ -f "$DATA" ]]; then
  COUNT=$(python3 -c "import json; d=json.load(open('$DATA')); print(len(d))" 2>/dev/null || echo "?")
  ok "Dataset encontrado — $COUNT filmes"
else
  fail "Dataset não encontrado: $DATA"
  echo "     → Execute ./quickstart.sh para gerar o dataset"
fi

# ── 6. Frontend — build ────────────────────────
echo ""
echo "▶ Frontend"
if [[ -d "$PROJECT_ROOT/frontend/node_modules" ]]; then
  ok "node_modules instalado"
else
  fail "node_modules não encontrado — execute: cd frontend && npm install"
fi

if command -v node &>/dev/null; then
  BUILD_OUT=$(cd "$PROJECT_ROOT/frontend" && npm run build 2>&1)
  if echo "$BUILD_OUT" | grep -qE "✓ built|built in"; then
    ok "Build do frontend concluído com sucesso"
  else
    fail "Build do frontend falhou"
    echo "$BUILD_OUT" | tail -5
  fi
else
  fail "Node.js não encontrado"
fi

# ── 7. API em execução (opcional) ─────────────
echo ""
echo "▶ API (verificação ao vivo)"
if command -v curl &>/dev/null; then
  HEALTH=$(curl -sf --max-time 3 http://localhost:8000/health 2>/dev/null || echo "")
  if [[ -n "$HEALTH" ]]; then
    MOVIES_COUNT=$(echo "$HEALTH" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d.get('movies',0))" 2>/dev/null || echo "?")
    ok "API respondendo — $MOVIES_COUNT filmes na memória"
  else
    echo "  ⚠️  API não está rodando (normal se iniciada separadamente)"
    echo "     → Para iniciar: cd backend && uvicorn app.main:app --reload"
  fi
fi

# ── Resumo ──────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Resultado: $PASS verificações OK, $FAIL falhas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
[[ $FAIL -gt 0 ]] && exit 1 || exit 0
