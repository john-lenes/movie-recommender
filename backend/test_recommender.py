from app.data import build_dataset
from app.recommender import ContentBasedRecommender

movies = build_dataset()
rec = ContentBasedRecommender(movies)
print("✅ Algoritmo aprimorado inicializado com sucesso!")
print()

# Testar com filmes clássicos
test_cases = [
    (278, "The Shawshank Redemption"),
    (238, "The Godfather"),
    (424, "Schindler's List"),
]

for movie_id, title in test_cases:
    results = rec.recommend([movie_id], [], k=5)
    liked_movie = next((m for m in movies if m["id"] == movie_id), None)

    print(
        f'🎬 Filme curtido: {liked_movie["title"]} ({liked_movie.get("year", "N/A")})'
    )
    print(f'   Gêneros: {", ".join(liked_movie.get("genres", []))}')
    print(f'   Keywords: {", ".join(liked_movie.get("keywords", [])[:3])}')
    print()
    print("   Top 3 Recomendações:")
    for i, r in enumerate(results[:3]):
        print(
            f'   {i+1}. {r[0]["title"]} ({r[0].get("year", "N/A")}) - Score: {r[1]:.3f}'
        )
        print(f"      {r[2]}")
    print()
    print("-" * 80)
    print()
