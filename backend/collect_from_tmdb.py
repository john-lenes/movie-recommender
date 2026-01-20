"""
Script para coletar filmes diretamente da API do TMDB
Expande o catálogo com filmes populares, bem avaliados e recentes
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    print("❌ TMDB_API_KEY não encontrada no .env")
    exit(1)

# Caminhos
DATA_DIR = Path("./data")
OUTPUT_FILE = DATA_DIR / "movies_enriched.json"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Configurações
MOVIES_PER_CATEGORY = 20  # Filmes por categoria
RATE_LIMIT_DELAY = 0.25  # 4 requisições por segundo


def get_tmdb_data(endpoint: str, params: dict = None) -> dict:
    """Faz requisição à API do TMDB"""
    base_url = "https://api.themoviedb.org/3"
    url = f"{base_url}/{endpoint}"

    default_params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}

    if params:
        default_params.update(params)

    try:
        response = requests.get(url, params=default_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        time.sleep(RATE_LIMIT_DELAY)

        # Validar resposta
        if not isinstance(data, dict):
            print(f"  ⚠️  Resposta inválida de {endpoint}")
            return {}

        return data
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro de rede em {endpoint}: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"  ⚠️  Erro ao decodificar JSON de {endpoint}: {e}")
        return {}
    except Exception as e:
        print(f"  ⚠️  Erro inesperado em {endpoint}: {e}")
        return {}


def get_movie_full_details(tmdb_id: int) -> Dict:
    """Busca todos os detalhes de um filme"""
    cache_file = CACHE_DIR / f"movie_{tmdb_id}_full.json"

    # Usar cache se existir
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # Buscar detalhes completos
    params = {"append_to_response": "credits,keywords,release_dates"}

    data = get_tmdb_data(f"movie/{tmdb_id}", params)

    if data:
        # Salvar no cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def extract_us_certification(release_dates_data: dict) -> str:
    """Extrai a certificação dos EUA (PG, PG-13, R, etc)"""
    if not release_dates_data or "results" not in release_dates_data:
        return None

    for country in release_dates_data["results"]:
        if country.get("iso_3166_1") == "US":
            for release in country.get("release_dates", []):
                cert = release.get("certification")
                if cert:
                    return cert
    return None


def parse_movie_data(data: Dict, movie_id: int) -> Optional[Dict]:
    """Converte dados do TMDB para formato do sistema"""
    if not data or not data.get("title"):
        return None

    if not isinstance(movie_id, int) or movie_id < 1:
        print(f"  ⚠️  ID de filme inválido: {movie_id}")
        return None

    # Extrair ano do release_date
    year = 2020
    if data.get("release_date"):
        try:
            year = int(data["release_date"][:4])
        except (ValueError, TypeError) as e:
            print(f"  ⚠️  Erro ao parsear ano de '{data.get('release_date')}': {e}")
            year = 2020

    # Gêneros (traduzidos)
    genres_map = {
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

    genres = [genres_map.get(g["name"], g["name"]) for g in data.get("genres", [])]
    tmdb_genres = [g["name"] for g in data.get("genres", [])]

    # Diretor
    director = "Desconhecido"
    credits = data.get("credits", {})
    crew = credits.get("crew", [])
    for person in crew:
        if person.get("job") == "Director":
            director = person.get("name", "Desconhecido")
            break

    # Elenco (top 20)
    cast = [
        actor.get("name") for actor in credits.get("cast", [])[:20] if actor.get("name")
    ]

    # Keywords
    keywords_data = data.get("keywords", {})
    keywords = [
        kw.get("name") for kw in keywords_data.get("keywords", []) if kw.get("name")
    ]

    # Production companies
    companies = [
        c.get("name") for c in data.get("production_companies", []) if c.get("name")
    ]

    # Production countries
    countries = [
        c.get("name") for c in data.get("production_countries", []) if c.get("name")
    ]

    # Spoken languages
    spoken_languages = []
    for lang in data.get("spoken_languages", []):
        if lang.get("iso_639_1"):
            spoken_languages.append(
                {
                    "iso_639_1": lang["iso_639_1"],
                    "name": lang.get("name", ""),
                    "english_name": lang.get("english_name", ""),
                }
            )

    # Certificação
    certification = extract_us_certification(data.get("release_dates", {}))

    # Coleção
    belongs_to_collection = None
    if data.get("belongs_to_collection"):
        coll = data["belongs_to_collection"]
        belongs_to_collection = {
            "id": coll.get("id"),
            "name": coll.get("name"),
            "poster_path": coll.get("poster_path"),
            "backdrop_path": coll.get("backdrop_path"),
        }

    # Montar filme
    movie = {
        "id": movie_id,
        "title": data.get("title", "Sem título"),
        "year": year,
        "genres": genres,
        "director": director,
        "description": data.get("overview", ""),
        # IDs externos
        "tmdb_id": data.get("id"),
        "imdb_id": data.get("imdb_id"),
        # Informações básicas
        "original_title": data.get("original_title"),
        "original_language": data.get("original_language"),
        "overview": data.get("overview"),
        "tagline": data.get("tagline"),
        "runtime": data.get("runtime"),
        "release_date": data.get("release_date"),
        # Avaliações
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "popularity": data.get("popularity"),
        "rating_stats": None,  # Será preenchido se tiver dados do MovieLens
        # Conteúdo
        "keywords": keywords,
        "cast": cast,
        "production_companies": companies,
        "production_countries": countries,
        "tmdb_genres": tmdb_genres,
        # Imagens
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        # Flags
        "adult": data.get("adult"),
        "video": data.get("video"),
        # Financeiro
        "budget": data.get("budget") if data.get("budget") else None,
        "revenue": data.get("revenue") if data.get("revenue") else None,
        # Coleção
        "belongs_to_collection": belongs_to_collection,
        # Idiomas
        "spoken_languages": spoken_languages,
        "certification": certification,
        # Status
        "status": data.get("status"),
    }

    return movie


def discover_movies(category: str, page: int = 1) -> List[Dict]:
    """Descobre filmes por categoria"""

    if category == "popular":
        endpoint = "movie/popular"
        params = {"page": page}
    elif category == "top_rated":
        endpoint = "movie/top_rated"
        params = {"page": page}
    elif category == "now_playing":
        endpoint = "movie/now_playing"
        params = {"page": page}
    elif category == "upcoming":
        endpoint = "movie/upcoming"
        params = {"page": page}
    else:
        # Descoberta por gênero ou filtros
        endpoint = "discover/movie"
        params = {
            "page": page,
            "sort_by": "popularity.desc",
            "vote_count.gte": 100,
            "with_genres": category,
        }

    data = get_tmdb_data(endpoint, params)

    if not data:
        print(f"  ⚠️  Nenhum dado retornado para categoria {category}")
        return []

    results = data.get("results", [])
    if not isinstance(results, list):
        print(f"  ⚠️  Formato de resultados inválido para {category}")
        return []

    return results


def main():
    print("🎬 Coletando filmes da API do TMDB...\n")

    # Carregar filmes existentes
    existing_movies = []
    existing_tmdb_ids = set()

    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_movies = json.load(f)
            existing_tmdb_ids = {
                m.get("tmdb_id") for m in existing_movies if m.get("tmdb_id")
            }
        print(f"📊 {len(existing_movies)} filmes existentes no catálogo\n")

    # Próximo ID disponível
    try:
        next_id = (
            max(
                [m.get("id", 0) for m in existing_movies if isinstance(m, dict)],
                default=0,
            )
            + 1
        )
    except (ValueError, TypeError):
        print("⚠️  Erro ao determinar próximo ID, iniciando de 1")
        next_id = 1

    # Categorias para coletar
    categories = [
        ("popular", "Filmes Populares"),
        ("top_rated", "Mais Bem Avaliados"),
        ("now_playing", "Em Cartaz"),
        # Gêneros específicos
        ("28", "Ação"),
        ("35", "Comédia"),
        ("18", "Drama"),
        ("27", "Terror"),
        ("878", "Ficção Científica"),
        ("53", "Suspense"),
        ("10749", "Romance"),
        ("16", "Animação"),
    ]

    new_movies = []

    for category_id, category_name in categories:
        print(f"📂 Categoria: {category_name}")

        # Buscar filmes da categoria
        results = discover_movies(category_id, page=1)

        collected_count = 0
        for movie_data in results:
            if collected_count >= MOVIES_PER_CATEGORY:
                break

            tmdb_id = movie_data.get("id")
            if not tmdb_id or tmdb_id in existing_tmdb_ids:
                continue

            print(f"  🎬 {movie_data.get('title', 'Sem título')} (TMDB ID: {tmdb_id})")

            # Buscar detalhes completos
            full_data = get_movie_full_details(tmdb_id)

            if full_data:
                movie = parse_movie_data(full_data, next_id)

                if movie:
                    new_movies.append(movie)
                    existing_tmdb_ids.add(tmdb_id)
                    next_id += 1
                    collected_count += 1

                    # Mostrar info
                    if movie.get("vote_average"):
                        print(f"     ⭐ {movie['vote_average']:.1f}/10")
                    if movie.get("budget"):
                        print(f"     💰 ${movie['budget']:,}")

        print(f"  ✅ {collected_count} novos filmes coletados\n")

    # Combinar filmes existentes com novos
    all_movies = existing_movies + new_movies

    # Salvar catálogo expandido
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Coleta concluída!")
    print(f"   📊 Total de filmes: {len(all_movies)}")
    print(f"   🆕 Novos filmes adicionados: {len(new_movies)}")
    print(f"   💾 Salvo em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
