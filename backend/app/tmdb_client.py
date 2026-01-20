"""
Cliente para The Movie Database (TMDB) API
Gerencia requisições, cache e busca de metadados de filmes
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()


class TMDBClient:
    """Cliente para interagir com TMDB API com cache inteligente"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self):
        # Credenciais TMDB (fallback para valores padrão se .env não existir)
        self.api_key = os.getenv("TMDB_API_KEY", "063849745cebc73dd3d860ffdcfd9637")
        self.bearer_token = os.getenv(
            "TMDB_BEARER_TOKEN",
            "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNjM4NDk3NDVjZWJjNzNkZDNkODYwZmZkY2ZkOTYzNyIsIm5iZiI6MTc2ODg0NTE2Ny42NjksInN1YiI6IjY5NmU2ZjZmYzNjOTEzYjU4NzIwZGI0YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.JY8xyPRFazyUqOONvmmonk4iwjdxMWZ-qVjJKM2Fp8Q"
        )
        
        self.language = os.getenv("DEFAULT_LANGUAGE", "pt-BR")
        self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.cache_dir = Path(os.getenv("CACHE_DIR", "./data/cache"))
        self.cache_expiry_days = int(os.getenv("CACHE_EXPIRY_DAYS", "7"))
        
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Retorna caminho do arquivo de cache"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Verifica se cache ainda é válido"""
        if not cache_path.exists():
            return False
        
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        expiry = datetime.now() - timedelta(days=self.cache_expiry_days)
        return mtime > expiry
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Busca dados do cache se válido"""
        if not self.enable_cache:
            return None
        
        cache_path = self._get_cache_path(cache_key)
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao ler cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Salva dados no cache"""
        if not self.enable_cache:
            return
        
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição à API com rate limiting"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        params['language'] = self.language
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            time.sleep(0.25)  # Rate limiting: 4 req/s
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição TMDB: {e}")
            return None
    
    def search_movie(self, query: str, year: Optional[int] = None) -> Optional[Dict]:
        """Busca filme por título"""
        cache_key = f"search_{query}_{year or 'any'}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        params = {'query': query}
        if year:
            params['year'] = year
        
        data = self._make_request('/search/movie', params)
        if data and data.get('results'):
            result = data['results'][0]  # Primeiro resultado
            self._save_to_cache(cache_key, result)
            return result
        return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Busca detalhes completos de um filme"""
        cache_key = f"movie_{tmdb_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        data = self._make_request(
            f'/movie/{tmdb_id}',
            params={'append_to_response': 'credits,keywords,videos'}
        )
        
        if data:
            self._save_to_cache(cache_key, data)
        return data
    
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Busca filmes populares"""
        cache_key = f"popular_page_{page}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('results', [])
        
        data = self._make_request('/movie/popular', params={'page': page})
        if data:
            self._save_to_cache(cache_key, data)
            return data.get('results', [])
        return []
    
    def get_top_rated_movies(self, page: int = 1) -> List[Dict]:
        """Busca filmes mais bem avaliados"""
        cache_key = f"top_rated_page_{page}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('results', [])
        
        data = self._make_request('/movie/top_rated', params={'page': page})
        if data:
            self._save_to_cache(cache_key, data)
            return data.get('results', [])
        return []
    
    def enrich_movie_data(self, movie_basic: Dict) -> Dict:
        """Enriquece dados básicos do filme com detalhes do TMDB"""
        tmdb_id = movie_basic.get('tmdb_id')
        if not tmdb_id:
            # Tenta buscar por título e ano
            search_result = self.search_movie(
                movie_basic.get('title', ''),
                movie_basic.get('year')
            )
            if search_result:
                tmdb_id = search_result['id']
        
        if not tmdb_id:
            return movie_basic
        
        details = self.get_movie_details(tmdb_id)
        if not details:
            return movie_basic
        
        # Extrair informações relevantes
        enriched = {
            **movie_basic,
            'tmdb_id': tmdb_id,
            'title': details.get('title', movie_basic.get('title')),
            'original_title': details.get('original_title'),
            'overview': details.get('overview', movie_basic.get('description', '')),
            'genres': [g['name'] for g in details.get('genres', [])],
            'release_date': details.get('release_date'),
            'year': int(details.get('release_date', '0000')[:4]) if details.get('release_date') else None,
            'runtime': details.get('runtime'),
            'vote_average': details.get('vote_average'),
            'vote_count': details.get('vote_count'),
            'popularity': details.get('popularity'),
            'poster_path': details.get('poster_path'),
            'backdrop_path': details.get('backdrop_path'),
        }
        
        # Créditos (diretor e elenco)
        credits = details.get('credits', {})
        crew = credits.get('crew', [])
        directors = [c['name'] for c in crew if c.get('job') == 'Director']
        if directors:
            enriched['director'] = directors[0]
        
        cast = credits.get('cast', [])[:5]  # Top 5 atores
        enriched['cast'] = [c['name'] for c in cast]
        
        # Keywords (tags)
        keywords = details.get('keywords', {}).get('keywords', [])
        enriched['keywords'] = [k['name'] for k in keywords[:20]]  # Top 20 keywords
        
        return enriched
    
    def get_poster_url(self, poster_path: Optional[str]) -> Optional[str]:
        """Retorna URL completa do poster"""
        if poster_path:
            return f"{self.IMAGE_BASE_URL}{poster_path}"
        return None


# Singleton instance
_tmdb_client = None

def get_tmdb_client() -> TMDBClient:
    """Retorna instância singleton do cliente TMDB"""
    global _tmdb_client
    if _tmdb_client is None:
        _tmdb_client = TMDBClient()
    return _tmdb_client
