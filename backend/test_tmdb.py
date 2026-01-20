#!/usr/bin/env python3
"""
Teste rápido da integração TMDB - busca alguns filmes populares
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.tmdb_client import TMDBClient

# Configurar credenciais
os.environ['TMDB_API_KEY'] = '063849745cebc73dd3d860ffdcfd9637'

def test_tmdb_integration():
    """Testa integração com TMDB buscando filmes populares"""
    print("="*60)
    print("🎬 Teste de Integração TMDB")
    print("="*60)
    
    tmdb = TMDBClient()
    
    # Lista de filmes para testar
    test_movies = [
        ("Matrix", 1999),
        ("Cidade de Deus", 2002),
        ("Inception", 2010),
        ("Tropa de Elite", 2007),
        ("Parasita", 2019),
    ]
    
    enriched_movies = []
    
    for title, year in test_movies:
        print(f"\n🔍 Buscando: {title} ({year})")
        
        # Buscar filme
        search_result = tmdb.search_movie(title, year)
        
        if not search_result:
            print(f"   ❌ Não encontrado")
            continue
        
        movie_id = search_result["id"]
        print(f"   ✅ Encontrado: {search_result['title']}")
        print(f"   📊 ID: {movie_id} | Nota: {search_result.get('vote_average', 0)}/10")
        
        # Obter detalhes completos
        details = tmdb.get_movie_details(movie_id)
        
        if details:
            # Extrair informações relevantes
            movie_data = {
                "id": movie_id,
                "title": details["title"],
                "original_title": details.get("original_title"),
                "year": int(details["release_date"][:4]) if details.get("release_date") else year,
                "overview": details.get("overview", "")[:200] + "...",
                "genres": [g["name"] for g in details.get("genres", [])],
                "vote_average": details.get("vote_average"),
                "runtime": details.get("runtime"),
                "poster_path": details.get("poster_path"),
            }
            
            # Buscar keywords
            keywords_data = tmdb._make_request(f"/movie/{movie_id}/keywords")
            if keywords_data and "keywords" in keywords_data:
                movie_data["keywords"] = [kw["name"] for kw in keywords_data["keywords"][:10]]
            
            # Buscar créditos
            credits_data = tmdb._make_request(f"/movie/{movie_id}/credits")
            if credits_data:
                # Diretor
                if "crew" in credits_data:
                    directors = [p["name"] for p in credits_data["crew"] if p.get("job") == "Director"]
                    if directors:
                        movie_data["director"] = directors[0]
                
                # Elenco
                if "cast" in credits_data:
                    movie_data["cast"] = [p["name"] for p in credits_data["cast"][:5]]
            
            enriched_movies.append(movie_data)
            
            # Mostrar informações
            print(f"   📝 Sinopse: {movie_data['overview']}")
            print(f"   🎭 Gêneros: {', '.join(movie_data['genres'])}")
            if "director" in movie_data:
                print(f"   🎥 Diretor: {movie_data['director']}")
            if "cast" in movie_data:
                print(f"   ⭐ Elenco: {', '.join(movie_data['cast'][:3])}")
            if "keywords" in movie_data:
                print(f"   🏷️  Keywords: {', '.join(movie_data['keywords'][:5])}")
    
    # Resumo
    print("\n" + "="*60)
    print(f"✅ Teste concluído!")
    print(f"📊 Filmes enriquecidos: {len(enriched_movies)}/{len(test_movies)}")
    print("="*60)
    
    # Salvar exemplo
    import json
    output_file = Path("./data/tmdb_test_sample.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_movies, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Dados de exemplo salvos em: {output_file}")
    
    return enriched_movies


if __name__ == "__main__":
    try:
        movies = test_tmdb_integration()
        
        print("\n🚀 Próximos passos:")
        print("   1. Execute setup_data.py para baixar MovieLens")
        print("   2. O script irá enriquecer todos os filmes com TMDB")
        print("   3. Inicie o servidor: uvicorn app.main:app --reload")
        
    except KeyboardInterrupt:
        print("\n⚠️  Teste cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
