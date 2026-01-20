"""
Script para configurar e popular o banco de dados com dados do MovieLens + TMDB
Execute: python -m app.setup_data
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

from app.movielens_loader import get_movielens_loader
from app.tmdb_client import get_tmdb_client

load_dotenv()


def setup_data():
    """Configura dados iniciais do sistema"""
    
    print("\n" + "="*60)
    print("🎬 CONFIGURAÇÃO DE DADOS - MovieLens + TMDB")
    print("="*60)
    
    # Verificar chave API do TMDB
    if not os.getenv("TMDB_API_KEY"):
        print("\n❌ ERRO: TMDB_API_KEY não configurada!")
        print("\n📝 Passos para configurar:")
        print("   1. Acesse: https://www.themoviedb.org/settings/api")
        print("   2. Crie uma conta gratuita")
        print("   3. Gere uma API Key")
        print("   4. Copie backend/.env.example para backend/.env")
        print("   5. Adicione sua chave no arquivo .env")
        return False
    
    # Inicializar clientes
    try:
        tmdb_client = get_tmdb_client()
        print("\n✅ Cliente TMDB inicializado")
    except Exception as e:
        print(f"\n❌ Erro ao inicializar TMDB: {e}")
        return False
    
    movielens_loader = get_movielens_loader()
    
    # Carregar dados do MovieLens
    if not movielens_loader.load_all():
        print("\n⚠️  Dados do MovieLens não encontrados ou incompletos")
        print("\n📥 Baixe o dataset MovieLens:")
        print("   1. Acesse: https://grouplens.org/datasets/movielens/")
        print("   2. Baixe 'ml-latest-small.zip' (recomendado para teste)")
        print("   3. Extraia em: backend/data/movielens/")
        print("   4. Estrutura esperada:")
        print("      backend/data/movielens/")
        print("      ├── movies.csv")
        print("      ├── ratings.csv")
        print("      └── links.csv")
        
        # Usar dados mock para demonstração
        print("\n💡 Usando dados mock para demonstração...")
        return create_mock_data(tmdb_client)
    
    # Buscar filmes populares e bem avaliados
    print("\n📊 Selecionando melhores filmes...")
    
    # Pegar mix de populares e bem avaliados
    popular = movielens_loader.get_popular_movies(limit=50)
    top_rated = movielens_loader.get_top_rated_movies(min_ratings=50, limit=50)
    
    # Combinar e remover duplicatas
    movies_dict = {}
    for movie in popular + top_rated:
        movies_dict[movie['id']] = movie
    
    movies = list(movies_dict.values())[:100]  # Limitar a 100
    
    # Enriquecer com dados do TMDB
    enriched_movies = movielens_loader.combine_with_tmdb(movies, tmdb_client)
    
    # Salvar em arquivo JSON
    output_dir = Path("./data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "movies_enriched.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_movies, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados salvos em: {output_file}")
    print(f"📊 Total de filmes: {len(enriched_movies)}")
    
    # Estatísticas
    with_posters = sum(1 for m in enriched_movies if m.get('poster_path'))
    with_keywords = sum(1 for m in enriched_movies if m.get('keywords'))
    with_cast = sum(1 for m in enriched_movies if m.get('cast'))
    
    print(f"\n📈 Estatísticas:")
    print(f"   - Com posters: {with_posters}/{len(enriched_movies)}")
    print(f"   - Com keywords: {with_keywords}/{len(enriched_movies)}")
    print(f"   - Com elenco: {with_cast}/{len(enriched_movies)}")
    
    return True


def create_mock_data(tmdb_client):
    """Cria dados mock usando filmes populares do TMDB"""
    print("\n🎬 Buscando filmes populares do TMDB...")
    
    movies = []
    
    # Buscar páginas de filmes populares
    for page in range(1, 6):  # 5 páginas = ~100 filmes
        print(f"   Página {page}/5...")
        popular_movies = tmdb_client.get_popular_movies(page=page)
        
        for movie in popular_movies:
            enriched = tmdb_client.enrich_movie_data({
                'tmdb_id': movie['id'],
                'title': movie['title']
            })
            movies.append(enriched)
    
    # Salvar
    output_dir = Path("./data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "movies_enriched.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados mock salvos em: {output_file}")
    print(f"📊 Total de filmes: {len(movies)}")
    
    return True


if __name__ == "__main__":
    success = setup_data()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n🚀 Agora você pode iniciar o servidor:")
        print("   uvicorn app.main:app --reload --port 8000")
    else:
        print("\n" + "="*60)
        print("❌ CONFIGURAÇÃO FALHOU")
        print("="*60)
        print("\n   Revise os erros acima e tente novamente.")
