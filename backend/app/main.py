from typing import Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .auth import get_token_manager
from .data import build_dataset
from .database import get_db
from .models import (
    AuthResponse,
    FeedbackIn,
    Movie,
    RatingIn,
    Recommendation,
    RecommendationResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from .recommender import ContentBasedRecommender

app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOVIES: List[Dict] = build_dataset()
RECOMMENDER = ContentBasedRecommender(MOVIES)
DB = get_db()
TOKEN_MANAGER = get_token_manager()


def get_current_user(authorization: Optional[str] = Header(None)):
    """Middleware para autenticação"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token inválido")

    token = authorization.replace("Bearer ", "")
    user_id = TOKEN_MANAGER.validate_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    user = DB.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user


@app.get("/health")
def health():
    return {"ok": True, "users": len(DB.users), "movies": len(MOVIES)}


@app.get("/movies", response_model=List[Movie])
def list_movies(
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_popularity: Optional[float] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    keyword: Optional[str] = None,
):
    """
    Lista filmes com filtros avançados
    - genre: Filtrar por gênero
    - min_rating: Avaliação mínima TMDB (vote_average)
    - min_popularity: Popularidade mínima TMDB
    - year_from/year_to: Intervalo de anos
    - keyword: Buscar por palavra-chave no título, overview ou keywords TMDB
    """
    results = MOVIES

    if genre:
        results = [
            m
            for m in results
            if genre.lower() in [g.lower() for g in m.get("genres", [])]
        ]

    if min_rating is not None:
        results = [
            m
            for m in results
            if m.get("vote_average") and m["vote_average"] >= min_rating
        ]

    if min_popularity is not None:
        results = [
            m
            for m in results
            if m.get("popularity") and m["popularity"] >= min_popularity
        ]

    if year_from is not None:
        results = [m for m in results if m.get("year", 0) >= year_from]

    if year_to is not None:
        results = [m for m in results if m.get("year", 9999) <= year_to]

    if keyword:
        keyword_lower = keyword.lower()
        results = [
            m
            for m in results
            if keyword_lower in m.get("title", "").lower()
            or keyword_lower in m.get("overview", "").lower()
            or any(keyword_lower in kw.lower() for kw in m.get("keywords", []))
        ]

    return results


@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie_details(movie_id: int):
    """Retorna detalhes completos de um filme específico"""
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    return movie


@app.get("/movies/{movie_id}/similar", response_model=List[Movie])
def get_similar_movies(movie_id: int, limit: int = 5):
    """
    Retorna filmes similares baseados em:
    - Gêneros em comum
    - Keywords compartilhadas
    - Mesmo diretor
    """
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    movie_genres = set(m.lower() for m in movie.get("genres", []))
    movie_keywords = set(kw.lower() for kw in movie.get("keywords", []))
    movie_director = movie.get("director", "").lower()

    # Calcular score de similaridade
    scored = []
    for m in MOVIES:
        if m["id"] == movie_id:
            continue

        score = 0.0
        m_genres = set(g.lower() for g in m.get("genres", []))
        m_keywords = set(kw.lower() for kw in m.get("keywords", []))
        m_director = m.get("director", "").lower()

        # Gêneros em comum (peso 3)
        genre_overlap = len(movie_genres & m_genres)
        score += genre_overlap * 3

        # Keywords em comum (peso 2)
        keyword_overlap = len(movie_keywords & m_keywords)
        score += keyword_overlap * 2

        # Mesmo diretor (peso 5)
        if movie_director and m_director == movie_director:
            score += 5

        if score > 0:
            scored.append((m, score))

    # Ordenar por score e retornar top N
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in scored[:limit]]


# ========== AUTH ENDPOINTS ==========


@app.post("/auth/register", response_model=AuthResponse)
def register(payload: UserCreate):
    """Registra novo usuário"""
    user = DB.create_user(
        username=payload.username, email=payload.email, password=payload.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou email já existe")

    token = TOKEN_MANAGER.create_token(user.id)

    return AuthResponse(user=UserResponse(**user.to_dict()), token=token)


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: UserLogin):
    """Login de usuário"""
    user = DB.authenticate(payload.username, payload.password)

    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    token = TOKEN_MANAGER.create_token(user.id)

    return AuthResponse(user=UserResponse(**user.to_dict()), token=token)


@app.post("/auth/logout")
def logout(authorization: str = Header(None)):
    """Logout de usuário"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        TOKEN_MANAGER.revoke_token(token)

    return {"ok": True}


@app.get("/auth/me", response_model=UserResponse)
def get_me(authorization: str = Header(None)):
    """Retorna dados do usuário atual"""
    user = get_current_user(authorization)
    return UserResponse(**user.to_dict())


# ========== USER FEEDBACK ENDPOINTS ==========


@app.post("/feedback")
def feedback(payload: FeedbackIn, authorization: str = Header(None)):
    """Registra like/dislike de filme"""
    user = get_current_user(authorization)

    mid = int(payload.movie_id)
    action = payload.action.strip().lower()

    if action not in {"like", "dislike"}:
        raise HTTPException(status_code=400, detail="action must be like or dislike")

    if action == "like":
        DB.add_like(user.id, mid)
    else:
        DB.add_dislike(user.id, mid)

    return {"ok": True, "user": UserResponse(**user.to_dict())}


@app.post("/rating")
def rate_movie(payload: RatingIn, authorization: str = Header(None)):
    """Registra avaliação de filme"""
    user = get_current_user(authorization)

    if not (1 <= payload.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    DB.add_rating(user.id, payload.movie_id, payload.rating)

    return {"ok": True, "user": UserResponse(**user.to_dict())}


@app.delete("/feedback/{movie_id}")
def remove_feedback(movie_id: int, authorization: str = Header(None)):
    """Remove feedback de filme"""
    user = get_current_user(authorization)
    DB.remove_feedback(user.id, movie_id)

    return {"ok": True, "user": UserResponse(**user.to_dict())}


# ========== RECOMMENDATIONS ENDPOINT ==========


@app.get("/recommendations", response_model=RecommendationResponse)
def recommendations(k: int = 10, authorization: str = Header(None)):
    """Retorna recomendações personalizadas baseadas em filmes curtidos"""
    user = get_current_user(authorization)

    liked_ids = user.liked_movies
    disliked_ids = user.disliked_movies

    recs = RECOMMENDER.recommend(liked_ids=liked_ids, disliked_ids=disliked_ids, k=k)
    out = [Recommendation(movie=r[0], score=r[1], reason=r[2]) for r in recs]

    return RecommendationResponse(liked_ids=liked_ids, recommendations=out)
