#!/usr/bin/env python3
"""
Script para setup inicial: baixa MovieLens e enriquece com TMDB
"""
import os
import sys
import zipfile
from pathlib import Path
import requests
from tqdm import tqdm

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.movielens_loader import MovieLensLoader
from app.tmdb_client import TMDBClient
from app.data_enricher import DataEnricher


def download_file(url: str, dest_path: Path):
    """Baixa arquivo com barra de progresso"""
    print(f"📥 Baixando de {url}")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as f, tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        desc=dest_path.name
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))
    
    print(f"✅ Download completo: {dest_path}")


def download_movielens(data_dir: Path, dataset: str = "ml-latest-small"):
    """
    Baixa dataset do MovieLens
    
    Datasets disponíveis:
    - ml-latest-small: 100k ratings, 9k filmes
    - ml-latest: 27M ratings, 58k filmes (maior)
    """
    datasets = {
        "ml-latest-small": "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip",
        "ml-latest": "https://files.grouplens.org/datasets/movielens/ml-latest.zip"
    }
    
    if dataset not in datasets:
        print(f"❌ Dataset inválido: {dataset}")
        print(f"Disponíveis: {', '.join(datasets.keys())}")
        return False
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = data_dir / f"{dataset}.zip"
    extract_dir = data_dir / dataset
    
    # Verificar se já existe
    if extract_dir.exists() and (extract_dir / "movies.csv").exists():
        print(f"✅ MovieLens já existe em {extract_dir}")
        return True
    
    # Baixar
    try:
        download_file(datasets[dataset], zip_path)
    except Exception as e:
        print(f"❌ Erro ao baixar: {e}")
        return False
    
    # Extrair
    print(f"📦 Extraindo {zip_path.name}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print(f"✅ Extraído para {data_dir}")
        
        # Remover zip
        zip_path.unlink()
        print(f"🗑️  Removido {zip_path.name}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao extrair: {e}")
        return False


def enrich_with_tmdb(movielens_path: Path, output_path: Path, sample_size: int = None):
    """
    Enriquece dados do MovieLens com metadados do TMDB
    
    Args:
        movielens_path: Diretório com arquivos MovieLens
        output_path: Arquivo de saída JSON
        sample_size: Se especificado, processa apenas N filmes (para testes)
    """
    print("\n🎬 Iniciando enriquecimento com TMDB...")
    
    # Carregar MovieLens
    loader = MovieLensLoader(str(movielens_path))
    movies = loader.load_movies()
    ratings = loader.load_ratings()
    links = loader.load_links()
    
    if not movies:
        print("❌ Nenhum filme carregado do MovieLens")
        return False
    
    # Filtrar para sample se necessário
    if sample_size:
        print(f"📊 Processando apenas {sample_size} filmes (sample)")
        movie_ids = list(movies.keys())[:sample_size]
        movies = {mid: movies[mid] for mid in movie_ids}
    
    # Enriquecer com TMDB
    print(f"🔍 Enriquecendo {len(movies)} filmes com TMDB...")
    
    tmdb = TMDBClient()
    enricher = DataEnricher(tmdb, loader)
    
    enriched_movies = enricher.enrich_all_movies(
        movies,
        ratings,
        links,
        min_rating_count=10
    )
    
    # Salvar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enricher.save_enriched_data(enriched_movies, output_path)
    
    print(f"\n✅ Processo concluído!")
    print(f"📁 Dados salvos em: {output_path}")
    print(f"📊 Total de filmes enriquecidos: {len(enriched_movies)}")
    
    return True


def main():
    """Executa setup completo"""
    print("="*60)
    print("🎬 Setup do Sistema de Recomendação - TMDB + MovieLens")
    print("="*60)
    
    # Configurações
    data_dir = Path("./data")
    movielens_dataset = os.getenv("MOVIELENS_DATASET", "ml-latest-small")
    movielens_dir = data_dir / "movielens" / movielens_dataset
    output_file = data_dir / "enriched_movies.json"
    
    # Verificar credenciais TMDB
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("\n⚠️  TMDB_API_KEY não encontrada!")
        print("Crie um arquivo .env com:")
        print("TMDB_API_KEY=sua_chave_aqui")
        print("\nObtenha sua chave em: https://www.themoviedb.org/settings/api")
        return 1
    
    # Passo 1: Baixar MovieLens
    print("\n📥 PASSO 1: Download do MovieLens")
    if not download_movielens(data_dir / "movielens", movielens_dataset):
        return 1
    
    # Passo 2: Enriquecer com TMDB
    print("\n🔍 PASSO 2: Enriquecimento com TMDB")
    
    # Perguntar sobre sample
    print("\nOpcão de processamento:")
    print("1. Processar todos os filmes (pode demorar)")
    print("2. Processar apenas 100 filmes (teste rápido)")
    
    choice = input("\nEscolha (1 ou 2): ").strip()
    sample_size = 100 if choice == "2" else None
    
    if not enrich_with_tmdb(movielens_dir, output_file, sample_size):
        return 1
    
    print("\n" + "="*60)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print(f"\n📁 Dados prontos em: {output_file}")
    print("\n🚀 Próximos passos:")
    print("   1. cd backend")
    print("   2. uvicorn app.main:app --reload")
    print("\n   Ou use: ./run.sh")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
