from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr


class RatingStats(BaseModel):
    """Estatísticas de avaliação do MovieLens"""

    average: Optional[float] = None
    count: Optional[int] = None
    min: Optional[float] = None
    max: Optional[float] = None


class CollectionInfo(BaseModel):
    """Informações sobre coleção/franquia"""

    id: Optional[int] = None
    name: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None


class SpokenLanguage(BaseModel):
    """Idiomas falados no filme"""

    iso_639_1: str
    name: str
    english_name: Optional[str] = None


class Movie(BaseModel):
    id: int
    title: str
    year: int
    genres: List[str]
    director: str
    description: str

    # IDs externos
    tmdb_id: Optional[int] = None
    imdb_id: Optional[str] = None

    # Informações básicas TMDB
    original_title: Optional[str] = None
    original_language: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    runtime: Optional[int] = None
    release_date: Optional[str] = None

    # Avaliações e popularidade
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None
    rating_stats: Optional[RatingStats] = None

    # Conteúdo rico
    keywords: Optional[List[str]] = None
    cast: Optional[List[str]] = None
    production_companies: Optional[List[str]] = None
    production_countries: Optional[List[str]] = None

    # Imagens
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None

    # Flags
    adult: Optional[bool] = None
    video: Optional[bool] = None

    # Dados financeiros
    budget: Optional[int] = None
    revenue: Optional[int] = None

    # Coleção/Franquia
    belongs_to_collection: Optional[CollectionInfo] = None

    # Idiomas e certificação
    spoken_languages: Optional[List[SpokenLanguage]] = None
    original_language_name: Optional[str] = None
    certification: Optional[str] = None  # PG, PG-13, R, etc

    # Status do filme
    status: Optional[str] = None  # Released, Post Production, etc

    # Métricas derivadas (calculadas)
    roi: Optional[float] = None  # Return on Investment
    popularity_tier: Optional[str] = None  # Low, Medium, High, Viral
    decade: Optional[str] = None  # 1990s, 2000s, etc
    score_composite: Optional[float] = None  # Score ponderado TMDB + MovieLens
    trending_score: Optional[float] = None  # Baseado em popularidade + votos recentes


class FeedbackIn(BaseModel):
    movie_id: int
    action: str  # like | dislike


class RatingIn(BaseModel):
    movie_id: int
    rating: int  # 1-5


class Recommendation(BaseModel):
    movie: Movie
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    liked_ids: List[int]
    recommendations: List[Recommendation]


# User models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    liked_movies: List[int]
    disliked_movies: List[int]
    ratings: Dict[int, int]


class AuthResponse(BaseModel):
    user: UserResponse
    token: str
