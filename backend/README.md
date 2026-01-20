# Backend (FastAPI)

## Rodar local

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- `GET /movies` lista filmes
- `POST /feedback` com `{ "movie_id": 1, "action": "like" }`
- `GET /recommendations?k=10` recomenda com explicação
