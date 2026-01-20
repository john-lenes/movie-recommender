"""
Carregador e processador de dados do MovieLens
Combina ratings do MovieLens com metadados do TMDB
"""
import os
import csv
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()


class MovieLensLoader:
    """Carrega e processa dados do MovieLens"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path or os.getenv("MOVIELENS_PATH", "./data/movielens"))
        self.movies: Dict[int, Dict] = {}
        self.ratings: Dict[int, List[float]] = defaultdict(list)
        self.links: Dict[int, Dict] = {}
    
    def load_movies(self) -> Dict[int, Dict]:
        """Carrega arquivo movies.csv"""
        movies_file = self.data_path / "movies.csv"
        
        if not movies_file.exists():
            print(f"⚠️  Arquivo não encontrado: {movies_file}")
            print("📥 Baixe MovieLens em: https://grouplens.org/datasets/movielens/")
            return {}
        
        movies = {}
        try:
            with open(movies_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    movie_id = int(row['movieId'])
                    title_with_year = row['title']
                    
                    # Extrair ano do título (formato: "Title (YYYY)")
                    year = None
                    title = title_with_year
                    if title_with_year.endswith(')') and '(' in title_with_year:
                        parts = title_with_year.rsplit('(', 1)
                        if len(parts) == 2:
                            title = parts[0].strip()
                            year_str = parts[1].replace(')', '').strip()
                            try:
                                year = int(year_str)
                            except ValueError:
                                pass
                    
                    movies[movie_id] = {
                        'id': movie_id,
                        'title': title,
                        'year': year,
                        'genres': row['genres'].split('|') if row['genres'] != '(no genres listed)' else []
                    }
            
            self.movies = movies
            print(f"✅ Carregados {len(movies)} filmes do MovieLens")
            return movies
        
        except Exception as e:
            print(f"❌ Erro ao carregar movies.csv: {e}")
            return {}
    
    def load_ratings(self) -> Dict[int, List[float]]:
        """Carrega arquivo ratings.csv e agrega por filme"""
        ratings_file = self.data_path / "ratings.csv"
        
        if not ratings_file.exists():
            print(f"⚠️  Arquivo não encontrado: {ratings_file}")
            return {}
        
        ratings = defaultdict(list)
        try:
            with open(ratings_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    movie_id = int(row['movieId'])
                    rating = float(row['rating'])
                    ratings[movie_id].append(rating)
            
            self.ratings = ratings
            print(f"✅ Carregadas avaliações de {len(ratings)} filmes")
            return dict(ratings)
        
        except Exception as e:
            print(f"❌ Erro ao carregar ratings.csv: {e}")
            return {}
    
    def load_links(self) -> Dict[int, Dict]:
        """Carrega arquivo links.csv (MovieLens ID → TMDB ID)"""
        links_file = self.data_path / "links.csv"
        
        if not links_file.exists():
            print(f"⚠️  Arquivo não encontrado: {links_file}")
            return {}
        
        links = {}
        try:
            with open(links_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    movie_id = int(row['movieId'])
                    links[movie_id] = {
                        'imdb_id': row.get('imdbId'),
                        'tmdb_id': int(row['tmdbId']) if row.get('tmdbId') else None
                    }
            
            self.links = links
            print(f"✅ Carregados links de {len(links)} filmes")
            return links
        
        except Exception as e:
            print(f"❌ Erro ao carregar links.csv: {e}")
            return {}
    
    def load_all(self) -> bool:
        """Carrega todos os arquivos do MovieLens"""
        print("\n📂 Carregando dados do MovieLens...")
        
        movies = self.load_movies()
        ratings = self.load_ratings()
        links = self.load_links()
        
        return bool(movies and ratings and links)
    
    def get_movie_stats(self, movie_id: int) -> Dict:
        """Retorna estatísticas de um filme"""
        if movie_id not in self.ratings:
            return {'count': 0, 'average': 0.0}
        
        ratings_list = self.ratings[movie_id]
        return {
            'count': len(ratings_list),
            'average': sum(ratings_list) / len(ratings_list),
            'min': min(ratings_list),
            'max': max(ratings_list)
        }
    
    def get_top_rated_movies(self, min_ratings: int = 100, limit: int = 100) -> List[Dict]:
        """Retorna filmes mais bem avaliados (com mínimo de avaliações)"""
        movie_scores = []
        
        for movie_id, movie in self.movies.items():
            if movie_id not in self.ratings:
                continue
            
            ratings_list = self.ratings[movie_id]
            if len(ratings_list) < min_ratings:
                continue
            
            avg_rating = sum(ratings_list) / len(ratings_list)
            
            movie_scores.append({
                **movie,
                'avg_rating': avg_rating,
                'num_ratings': len(ratings_list),
                'tmdb_id': self.links.get(movie_id, {}).get('tmdb_id')
            })
        
        # Ordenar por média de avaliação e número de avaliações
        movie_scores.sort(key=lambda x: (x['avg_rating'], x['num_ratings']), reverse=True)
        
        return movie_scores[:limit]
    
    def get_popular_movies(self, limit: int = 100) -> List[Dict]:
        """Retorna filmes mais populares (mais avaliados)"""
        movie_scores = []
        
        for movie_id, movie in self.movies.items():
            if movie_id not in self.ratings:
                continue
            
            ratings_list = self.ratings[movie_id]
            avg_rating = sum(ratings_list) / len(ratings_list)
            
            movie_scores.append({
                **movie,
                'avg_rating': avg_rating,
                'num_ratings': len(ratings_list),
                'tmdb_id': self.links.get(movie_id, {}).get('tmdb_id')
            })
        
        # Ordenar por número de avaliações
        movie_scores.sort(key=lambda x: x['num_ratings'], reverse=True)
        
        return movie_scores[:limit]
    
    def combine_with_tmdb(self, movies: List[Dict], tmdb_client) -> List[Dict]:
        """Combina dados do MovieLens com metadados do TMDB"""
        enriched_movies = []
        
        print(f"\n🔄 Enriquecendo {len(movies)} filmes com dados do TMDB...")
        
        for i, movie in enumerate(movies, 1):
            if i % 10 == 0:
                print(f"   Processando {i}/{len(movies)}...")
            
            try:
                enriched = tmdb_client.enrich_movie_data(movie)
                enriched_movies.append(enriched)
            except Exception as e:
                print(f"   ⚠️  Erro ao enriquecer '{movie.get('title')}': {e}")
                enriched_movies.append(movie)
        
        print(f"✅ {len(enriched_movies)} filmes enriquecidos com sucesso!\n")
        return enriched_movies


# Singleton instance
_movielens_loader = None

def get_movielens_loader() -> MovieLensLoader:
    """Retorna instância singleton do loader MovieLens"""
    global _movielens_loader
    if _movielens_loader is None:
        _movielens_loader = MovieLensLoader()
    return _movielens_loader
