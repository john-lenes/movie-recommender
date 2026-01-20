"""
Script para enriquecer dados dos filmes com informações financeiras,
coleções, idiomas e certificações do TMDB
"""

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    print("❌ TMDB_API_KEY não encontrada no .env")
    exit(1)

# Caminhos dos arquivos
DATA_DIR = Path("./data")
INPUT_FILE = DATA_DIR / "movies_enriched.json"
OUTPUT_FILE = DATA_DIR / "movies_enriched.json"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def get_movie_details(tmdb_id: int) -> dict:
    """Busca detalhes completos do filme no TMDB"""
    cache_file = CACHE_DIR / f"movie_{tmdb_id}_full.json"

    # Usar cache se existir
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR",
        "append_to_response": "release_dates",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Salvar no cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        time.sleep(0.25)  # Rate limiting
        return data
    except Exception as e:
        print(f"  ⚠️  Erro ao buscar TMDB ID {tmdb_id}: {e}")
        return {}


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


def enrich_movie_with_financial_data(movie: dict) -> dict:
    """Enriquece um filme com dados financeiros e extras do TMDB"""
    tmdb_id = movie.get("tmdb_id")
    if not tmdb_id:
        return movie

    print(f"  🎬 {movie['title']} (TMDB ID: {tmdb_id})")

    # Buscar dados completos
    details = get_movie_details(tmdb_id)
    if not details:
        return movie

    # Dados financeiros
    if "budget" in details and details["budget"]:
        movie["budget"] = details["budget"]
        print(f"     💰 Budget: ${details['budget']:,}")

    if "revenue" in details and details["revenue"]:
        movie["revenue"] = details["revenue"]
        print(f"     💵 Revenue: ${details['revenue']:,}")

    # Coleção/Franquia
    if "belongs_to_collection" in details and details["belongs_to_collection"]:
        collection = details["belongs_to_collection"]
        movie["belongs_to_collection"] = {
            "id": collection.get("id"),
            "name": collection.get("name"),
            "poster_path": collection.get("poster_path"),
            "backdrop_path": collection.get("backdrop_path"),
        }
        print(f"     📚 Collection: {collection['name']}")

    # Idiomas falados
    if "spoken_languages" in details and details["spoken_languages"]:
        movie["spoken_languages"] = [
            {
                "iso_639_1": lang.get("iso_639_1"),
                "name": lang.get("name"),
                "english_name": lang.get("english_name"),
            }
            for lang in details["spoken_languages"]
        ]
        langs = ", ".join([l.get("name", "") for l in details["spoken_languages"][:3]])
        print(f"     🗣️  Languages: {langs}")

    # Status
    if "status" in details:
        movie["status"] = details["status"]

    # Certificação (rating etário)
    if "release_dates" in details:
        cert = extract_us_certification(details["release_dates"])
        if cert:
            movie["certification"] = cert
            print(f"     🔞 Certification: {cert}")

    return movie


def main():
    print("🎬 Enriquecendo dados financeiros e extras dos filmes...\n")

    # Carregar dados existentes
    if not INPUT_FILE.exists():
        print(f"❌ Arquivo não encontrado: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        movies = json.load(f)

    print(f"📊 Total de filmes: {len(movies)}\n")

    # Enriquecer cada filme
    enriched_count = 0
    for movie in movies:
        enriched = enrich_movie_with_financial_data(movie)
        if (
            enriched.get("budget")
            or enriched.get("revenue")
            or enriched.get("belongs_to_collection")
        ):
            enriched_count += 1

    # Salvar dados enriquecidos
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Enriquecimento concluído!")
    print(f"   📊 {enriched_count}/{len(movies)} filmes com novos dados")
    print(f"   💾 Salvo em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
