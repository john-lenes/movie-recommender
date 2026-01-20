"""
Enriquecedor de dados: combina MovieLens com TMDB
"""
import json
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

from .tmdb_client import TMDBClient
from .movielens_loader import MovieLensLoader


class DataEnricher:
    """Combina dados do MovieLens com metadados ricos do TMDB"""
    
    def __init__(self, tmdb_client: TMDBClient, movielens_loader: MovieLensLoader):
        self.tmdb = tmdb_client
        self.movielens = movielens_loader
    
    def calculate_rating_stats(self, ratings: List[float]) -> Dict:
        """Calcula estatísticas de avaliações"""
        if not ratings:
            return {
                "average": 0.0,
                "count": 0,
                "min": 0.0,
                "max": 0.0
            }
        
        return {
            "average": round(sum(ratings) / len(ratings), 2),
            "count": len(ratings),
            "min": min(ratings),
            "max": max(ratings)
        }
    
    def enrich_movie(
        self,
        movie: Dict,
        ratings: List[float] = None,
        tmdb_id: int = None
    ) -> Dict:
        """
        Enriquece um filme com dados do TMDB
        
        Args:
            movie: Dados básicos do MovieLens
            ratings: Lista de avaliações do filme
            tmdb_id: ID do TMDB (se disponível)
            
        Returns:
            Dicionário com dados enriquecidos
        """
        enriched = movie.copy()
        
        # Adicionar estatísticas de rating
        if ratings:
            enriched["rating_stats"] = self.calculate_rating_stats(ratings)
        
        # Buscar no TMDB
        tmdb_data = None
        
        if tmdb_id:
            # Usar ID direto se disponível
            tmdb_data = self.tmdb.get_movie_details(tmdb_id)
        else:
            # Buscar por título e ano
            search_result = self.tmdb.search_movie(
                movie["title"],
                movie.get("year")
            )
            if search_result:
                tmdb_data = self.tmdb.get_movie_details(search_result["id"])
        
        # Adicionar dados do TMDB
        if tmdb_data:
            enriched.update({
                "tmdb_id": tmdb_data["id"],
                "imdb_id": tmdb_data.get("imdb_id"),
                "original_title": tmdb_data.get("original_title"),
                "overview": tmdb_data.get("overview", ""),
                "tagline": tmdb_data.get("tagline", ""),
                "runtime": tmdb_data.get("runtime"),
                "vote_average": tmdb_data.get("vote_average"),
                "vote_count": tmdb_data.get("vote_count"),
                "popularity": tmdb_data.get("popularity"),
                "poster_path": tmdb_data.get("poster_path"),
                "backdrop_path": tmdb_data.get("backdrop_path"),
                "original_language": tmdb_data.get("original_language"),
                "adult": tmdb_data.get("adult", False),
                "video": tmdb_data.get("video", False),
                "release_date": tmdb_data.get("release_date"),
            })
            
            # Genres do TMDB (mais detalhados)
            if "genres" in tmdb_data:
                enriched["tmdb_genres"] = [g["name"] for g in tmdb_data["genres"]]
            
            # Keywords
            if "keywords" in tmdb_data and "keywords" in tmdb_data["keywords"]:
                enriched["keywords"] = [
                    kw["name"] for kw in tmdb_data["keywords"]["keywords"][:20]
                ]
            
            # Credits (diretor e elenco)
            if "credits" in tmdb_data:
                credits = tmdb_data["credits"]
                
                # Diretor
                if "crew" in credits:
                    directors = [
                        p["name"] for p in credits["crew"]
                        if p.get("job") == "Director"
                    ]
                    if directors:
                        enriched["director"] = directors[0]
                
                # Elenco principal (top 10)
                if "cast" in credits:
                    enriched["cast"] = [
                        p["name"] for p in credits["cast"][:10]
                    ]
            
            # Production companies
            if "production_companies" in tmdb_data:
                enriched["production_companies"] = [
                    pc["name"] for pc in tmdb_data["production_companies"][:5]
                ]
            
            # Production countries
            if "production_countries" in tmdb_data:
                enriched["production_countries"] = [
                    pc["name"] for pc in tmdb_data["production_countries"]
                ]
        
        return enriched
    
    def enrich_all_movies(
        self,
        movies: Dict[int, Dict],
        ratings: Dict[int, List[float]],
        links: Dict[int, Dict],
        min_rating_count: int = 10
    ) -> List[Dict]:
        """
        Enriquece todos os filmes
        
        Args:
            movies: Dicionário de filmes do MovieLens
            ratings: Avaliações por filme
            links: Links MovieLens → TMDB/IMDB
            min_rating_count: Número mínimo de avaliações para incluir filme
            
        Returns:
            Lista de filmes enriquecidos
        """
        enriched_movies = []
        
        # Filtrar filmes com avaliações suficientes
        filtered_ids = [
            mid for mid, movie in movies.items()
            if len(ratings.get(mid, [])) >= min_rating_count
        ]
        
        print(f"📊 Filmes após filtro ({min_rating_count}+ avaliações): {len(filtered_ids)}")
        
        # Enriquecer cada filme
        for movie_id in tqdm(filtered_ids, desc="Enriquecendo filmes"):
            movie = movies[movie_id]
            movie_ratings = ratings.get(movie_id, [])
            tmdb_id = links.get(movie_id, {}).get("tmdbId")
            
            try:
                enriched = self.enrich_movie(movie, movie_ratings, tmdb_id)
                enriched_movies.append(enriched)
            except Exception as e:
                print(f"\n⚠️  Erro ao enriquecer {movie['title']}: {e}")
                continue
        
        return enriched_movies
    
    def save_enriched_data(self, movies: List[Dict], output_path: Path):
        """Salva dados enriquecidos em JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Salvos {len(movies)} filmes em {output_path}")
    
    def load_enriched_data(self, input_path: Path) -> List[Dict]:
        """Carrega dados enriquecidos do JSON"""
        if not input_path.exists():
            return []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
