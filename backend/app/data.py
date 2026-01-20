# Dataset de filmes - usa dados do MovieLens + TMDB se disponível
# Caso contrário, usa dados mock em português brasileiro

import json
import math
from pathlib import Path
from typing import Dict, List


def calculate_derived_metrics(movie: Dict) -> None:
    """Calcula métricas derivadas para enriquecer os dados"""

    # ROI (Return on Investment)
    if movie.get("budget") and movie.get("revenue") and movie["budget"] > 0:
        movie["roi"] = round((movie["revenue"] / movie["budget"] - 1) * 100, 2)

    # Popularity Tier
    popularity = movie.get("popularity", 0)
    if popularity >= 50:
        movie["popularity_tier"] = "Viral"
    elif popularity >= 20:
        movie["popularity_tier"] = "High"
    elif popularity >= 5:
        movie["popularity_tier"] = "Medium"
    else:
        movie["popularity_tier"] = "Low"

    # Década
    year = movie.get("year")
    if year:
        decade_start = (year // 10) * 10
        movie["decade"] = f"{decade_start}s"

    # Score Composto (TMDB + MovieLens)
    tmdb_score = movie.get("vote_average", 0)
    ml_stats = movie.get("rating_stats", {})
    ml_score = ml_stats.get("average", 0) if isinstance(ml_stats, dict) else 0

    if tmdb_score and ml_score:
        # Normalizar MovieLens (0-5) para escala TMDB (0-10)
        ml_normalized = ml_score * 2
        # Média ponderada: TMDB 60%, MovieLens 40%
        movie["score_composite"] = round(tmdb_score * 0.6 + ml_normalized * 0.4, 2)
    elif tmdb_score:
        movie["score_composite"] = tmdb_score
    elif ml_score:
        movie["score_composite"] = ml_score * 2

    # Trending Score (popularidade + qualidade + votos)
    popularity = movie.get("popularity", 0)
    vote_avg = movie.get("vote_average", 0)
    vote_count = movie.get("vote_count", 0)

    if popularity and vote_avg and vote_count:
        # Fórmula: log(popularity) * vote_average * log(vote_count)
        pop_factor = math.log1p(popularity)
        vote_factor = math.log1p(vote_count)
        movie["trending_score"] = round(pop_factor * vote_avg * vote_factor / 10, 2)

    # Nome do idioma original
    lang_names = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ru": "Russian",
    }
    if movie.get("original_language"):
        movie["original_language_name"] = lang_names.get(
            movie["original_language"], movie["original_language"].upper()
        )


def build_dataset() -> List[Dict]:
    """
    Carrega dataset de filmes.
    Prioridade:
    1. Dados enriquecidos (MovieLens + TMDB) de movies_enriched.json
    2. Dados mock em português
    """

    # Tentar carregar dados enriquecidos
    enriched_file = Path("./data/movies_enriched.json")
    if enriched_file.exists():
        try:
            with open(enriched_file, "r", encoding="utf-8") as f:
                movies = json.load(f)
                print(f"✅ Carregados {len(movies)} filmes de {enriched_file}")

                # Adicionar IDs se necessário e normalizar estrutura
                for idx, m in enumerate(movies, start=1):
                    if "id" not in m:
                        m["id"] = idx

                    # Garantir campos obrigatórios
                    m.setdefault("title", "Sem título")
                    m.setdefault("year", 2020)
                    m.setdefault("genres", [])
                    m.setdefault("director", "Desconhecido")

                    # Usar overview se description não existir
                    if "description" not in m and "overview" in m:
                        m["description"] = m["overview"]
                    m.setdefault("description", "")

                    # Traduzir gêneros se estiverem em inglês
                    m["genres"] = translate_genres(m.get("genres", []))
                    if "tmdb_genres" in m:
                        m["tmdb_genres"] = translate_genres(m.get("tmdb_genres", []))

                    # Garantir todos os campos TMDB estão presentes (mesmo que None/vazios)
                    m.setdefault("tmdb_id", None)
                    m.setdefault("imdb_id", None)
                    m.setdefault("original_title", m.get("title"))
                    m.setdefault("original_language", None)
                    m.setdefault("overview", m.get("description"))
                    m.setdefault("tagline", None)
                    m.setdefault("runtime", None)
                    m.setdefault("release_date", None)
                    m.setdefault("vote_average", None)
                    m.setdefault("vote_count", None)
                    m.setdefault("popularity", None)
                    m.setdefault("rating_stats", None)
                    # Garantir listas não-None (usar lista vazia se None)
                    if m.get("keywords") is None:
                        m["keywords"] = []
                    if m.get("cast") is None:
                        m["cast"] = []
                    if m.get("production_companies") is None:
                        m["production_companies"] = []
                    if m.get("production_countries") is None:
                        m["production_countries"] = []
                    m.setdefault("poster_path", None)
                    m.setdefault("backdrop_path", None)
                    m.setdefault("adult", None)
                    m.setdefault("video", None)

                    # Campos financeiros
                    m.setdefault("budget", None)
                    m.setdefault("revenue", None)

                    # Coleção
                    m.setdefault("belongs_to_collection", None)

                    # Idiomas e certificação
                    if m.get("spoken_languages") is None:
                        m["spoken_languages"] = []
                    m.setdefault("original_language_name", None)
                    m.setdefault("certification", None)

                    # Status
                    m.setdefault("status", None)

                    # Calcular métricas derivadas
                    calculate_derived_metrics(m)

                return movies
        except Exception as e:
            print(f"⚠️  Erro ao carregar dados enriquecidos: {e}")
            print("   Usando dados mock...")

    # Fallback para dados mock
    return build_mock_dataset()


def translate_genres(genres: List[str]) -> List[str]:
    """Traduz gêneros do inglês para português"""
    translation = {
        "Action": "Ação",
        "Adventure": "Aventura",
        "Animation": "Animação",
        "Comedy": "Comédia",
        "Crime": "Crime",
        "Documentary": "Documentário",
        "Drama": "Drama",
        "Family": "Família",
        "Fantasy": "Fantasia",
        "History": "História",
        "Horror": "Terror",
        "Music": "Musical",
        "Mystery": "Mistério",
        "Romance": "Romance",
        "Science Fiction": "Ficção Científica",
        "TV Movie": "Filme para TV",
        "Thriller": "Suspense",
        "War": "Guerra",
        "Western": "Faroeste",
    }
    return [translation.get(g, g) for g in genres]


def build_mock_dataset() -> List[Dict]:
    base = [
        {
            "title": "A Noite do Assalto",
            "year": 2019,
            "genres": ["Ação", "Suspense"],
            "director": "Ana Kato",
            "description": "Uma equipe habilidosa planeja o roubo de um cofre high-tech em uma cidade neon.",
        },
        {
            "title": "Órbita Silenciosa",
            "year": 2021,
            "genres": ["Ficção Científica", "Drama"],
            "director": "Marcos Silva",
            "description": "Um astronauta confronta o isolamento e memórias perdidas em uma estação espacial defeituosa.",
        },
        {
            "title": "Café na Chuva",
            "year": 2017,
            "genres": ["Romance", "Comédia"],
            "director": "Laura Moreau",
            "description": "Dois estranhos se encontram durante uma tempestade e continuam se cruzando por acaso.",
        },
        {
            "title": "A Última Sequoia",
            "year": 2020,
            "genres": ["Aventura", "Drama"],
            "director": "João Park",
            "description": "Um guarda florestal e uma jornalista descobrem segredos em torno de uma floresta ancestral.",
        },
        {
            "title": "Sinais e Sombras",
            "year": 2018,
            "genres": ["Mistério", "Suspense"],
            "director": "Ricardo Nunes",
            "description": "Um detetive segue uma série de transmissões criptografadas ligadas a desaparecimentos.",
        },
        {
            "title": "Sala de Aula ao Amanhecer",
            "year": 2016,
            "genres": ["Drama", "Família"],
            "director": "Sandra Tan",
            "description": "Uma nova professora transforma a cultura de uma escola em dificuldades, um aluno por vez.",
        },
        {
            "title": "Receitas da Madrugada",
            "year": 2022,
            "genres": ["Comédia", "Família"],
            "director": "Paulo Duarte",
            "description": "Uma rivalidade de food trucks se transforma em amizade inesperada e um novo cardápio.",
        },
        {
            "title": "Porto das Engrenagens",
            "year": 2015,
            "genres": ["Fantasia", "Aventura"],
            "director": "Elena Collins",
            "description": "Uma cidade portuária funciona com engrenagens e magia; um entregador descobre um mapa oculto.",
        },
        {
            "title": "Ecos do Julgamento",
            "year": 2023,
            "genres": ["Drama", "Crime"],
            "director": "Vera Okoye",
            "description": "Uma defensora pública desvenda um caso que ameaça seu próprio passado.",
        },
        {
            "title": "Coração Pixelado",
            "year": 2014,
            "genres": ["Romance", "Drama"],
            "director": "Carlos Ito",
            "description": "Um designer de jogos e um músico colaboram e redescobrem o que realmente importa.",
        },
        {
            "title": "Entre Duas Cidades",
            "year": 2019,
            "genres": ["Drama", "Romance"],
            "director": "Beatriz Alves",
            "description": "Uma história de amor dividida entre São Paulo e o interior, explorando as diferenças culturais.",
        },
        {
            "title": "O Último Voo",
            "year": 2020,
            "genres": ["Ação", "Aventura"],
            "director": "Fernando Santos",
            "description": "Um piloto aposentado precisa fazer uma última missão para salvar sua família.",
        },
        {
            "title": "Samba nas Estrelas",
            "year": 2021,
            "genres": ["Musical", "Comédia"],
            "director": "Camila Rodrigues",
            "description": "Uma escola de samba do Rio se prepara para o carnaval com obstáculos inesperados.",
        },
        {
            "title": "Memórias de um Favelado",
            "year": 2018,
            "genres": ["Drama", "Biografia"],
            "director": "Roberto Lima",
            "description": "A jornada inspiradora de um jovem que sai da favela para se tornar médico.",
        },
        {
            "title": "Amazônia Perdida",
            "year": 2022,
            "genres": ["Aventura", "Documentário"],
            "director": "Marina Costa",
            "description": "Expedição na Amazônia revela segredos de civilizações perdidas e a luta pela preservação.",
        },
    ]

    # Expandir para 100 com variações controladas
    genres_pool = [
        "Ação",
        "Aventura",
        "Comédia",
        "Drama",
        "Ficção Científica",
        "Fantasia",
        "Suspense",
        "Mistério",
        "Crime",
        "Família",
        "Animação",
        "Terror",
        "Romance",
        "Musical",
        "Documentário",
        "Biografia",
    ]
    directors = [
        "Ana Kato",
        "Marcos Silva",
        "Laura Moreau",
        "João Park",
        "Ricardo Nunes",
        "Sandra Tan",
        "Paulo Duarte",
        "Elena Collins",
        "Vera Okoye",
        "Carlos Ito",
        "Natália Rahman",
        "Bruno Hansen",
        "Karina Almeida",
        "Daniel Novak",
        "Fernanda Souza",
        "Lucas Mendes",
        "Juliana Ferreira",
        "André Costa",
    ]

    dataset: List[Dict] = []
    dataset.extend(base)

    # Deterministic pseudo-generation
    for i in range(len(base), 100):
        g1 = genres_pool[i % len(genres_pool)]
        g2 = genres_pool[(i * 3 + 1) % len(genres_pool)]
        if g2 == g1:
            g2 = genres_pool[(i * 5 + 2) % len(genres_pool)]
        director = directors[(i * 7) % len(directors)]
        year = 2008 + (i % 17)
        dataset.append(
            {
                "title": f"Filme {i+1:03d}: Contos de {g1}",
                "year": year,
                "genres": sorted(list({g1, g2})),
                "director": director,
                "description": f"Uma história de {g1.lower()} com elementos de {g2.lower()}, dirigido por {director}.",
            }
        )

    # Adicionar IDs
    for idx, m in enumerate(dataset, start=1):
        m["id"] = idx

    return dataset
