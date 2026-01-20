from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _movie_to_text(movie: Dict) -> str:
    """
    Conteúdo usado para similaridade: gêneros + diretor + keywords + elenco + popularidade
    Com dados enriquecidos do TMDB, temos muito mais informação!
    """
    # Gêneros (peso alto)
    genres = " ".join([g.strip().lower() for g in movie.get("genres", [])])

    # Diretor (peso médio)
    director = movie.get("director", "").strip().lower().replace(".", "")

    # Keywords do TMDB (peso muito alto - são muito precisas para recomendação)
    keywords = " ".join([k.strip().lower() for k in movie.get("keywords", [])])

    # Elenco principal (top 10 atores)
    cast = " ".join([c.strip().lower() for c in movie.get("cast", [])[:10]])

    # Production companies (estúdios tem estilos próprios)
    companies = " ".join(
        [c.strip().lower() for c in movie.get("production_companies", [])]
    )

    # Overview/descrição (primeiras 200 palavras para não dominar)
    overview = movie.get("overview", movie.get("description", ""))
    if overview:
        words = overview.lower().split()[:200]
        overview_text = " ".join(words)
    else:
        overview_text = ""

    # Tagline (frases de efeito são muito descritivas)
    tagline = movie.get("tagline", "").lower()

    # Combinar tudo com pesos (repetindo para dar mais peso)
    parts = [
        f"generos:{genres} {genres} {genres}",  # Gêneros: peso 3x
        f"diretor:{director} {director}",  # Diretor: peso 2x
        f"keywords:{keywords} {keywords} {keywords} {keywords}",  # Keywords: peso 4x (muito importante!)
        f"elenco:{cast}",
        f"empresas:{companies}",
        f"tagline:{tagline}",
        f"sinopse:{overview_text}",
    ]

    return " ".join(parts)


class ContentBasedRecommender:
    def __init__(self, movies: List[Dict]):
        self.movies = movies
        self._vectorizer = TfidfVectorizer()
        corpus = [_movie_to_text(m) for m in movies]
        self._tfidf = self._vectorizer.fit_transform(corpus)

    def recommend(
        self, liked_ids: List[int], disliked_ids: List[int], k: int = 10
    ) -> List[Tuple[Dict, float, str]]:
        liked_set = set(liked_ids)
        disliked_set = set(disliked_ids)

        # Candidatos excluem curtidos/não curtidos
        candidates = [
            m
            for m in self.movies
            if m["id"] not in liked_set and m["id"] not in disliked_set
        ]

        if not liked_ids:
            # Se nada curtido ainda, retorna filmes populares e bem avaliados
            # Priorizar filmes com dados TMDB completos
            candidates_sorted = sorted(
                candidates,
                key=lambda x: (
                    -(x.get("popularity", 0) or 0),  # Popularidade TMDB
                    -(x.get("vote_average", 0) or 0),  # Avaliação TMDB
                    -x["year"],  # Mais recentes
                ),
            )
            out = []
            for m in candidates_sorted[:k]:
                rating = m.get("vote_average")
                popularity = m.get("popularity")

                reason_parts = ["💡 Filme popular e bem avaliado"]
                if rating:
                    reason_parts.append(f"⭐ {rating:.1f}/10 TMDB")
                if popularity:
                    reason_parts.append(f"🔥 {popularity:.0f} popularidade")

                out.append((m, 0.0, " · ".join(reason_parts)))
            return out

        # Construir perfil do usuário como média dos vetores dos filmes curtidos
        liked_idx = [lid - 1 for lid in liked_ids if 1 <= lid <= len(self.movies)]
        if not liked_idx:
            return []

        user_vec = self._tfidf[liked_idx].mean(axis=0)

        # Calcular similaridade com todos os filmes
        sims = cosine_similarity(user_vec, self._tfidf).ravel()

        # Penalizar filmes não curtidos mais fortemente
        for did in disliked_ids:
            if 1 <= did <= len(self.movies):
                sims[did - 1] *= 0.1

        # Aplicar boost de popularidade e qualidade (filmes bem avaliados são melhores recomendações)
        for idx, m in enumerate(self.movies):
            popularity_boost = 1.0
            if m.get("popularity"):
                # Boost suave baseado em popularidade (log scale para não dominar)
                popularity_boost = 1.0 + (np.log1p(m["popularity"]) / 50)

            quality_boost = 1.0
            if m.get("vote_average") and m.get("vote_count", 0) > 10:
                # Boost baseado em avaliação (apenas se tiver votos suficientes)
                quality_boost = 1.0 + ((m["vote_average"] - 5.0) / 20)  # Normalizado

            sims[idx] *= popularity_boost * quality_boost

        # Ranquear candidatos
        ranked = sorted(
            ((m, float(sims[m["id"] - 1])) for m in candidates),
            key=lambda t: t[1],
            reverse=True,
        )

        # Aplicar re-ranking para diversidade
        diverse_recs = []
        seen_directors = set()
        seen_companies = set()

        for m, score in ranked:
            # Boost para diretores ainda não vistos
            diversity_boost = 1.0
            if m.get("director") and m["director"] not in seen_directors:
                diversity_boost *= 1.15

            # Boost para production companies diferentes (variedade de estúdios)
            if m.get("production_companies"):
                company_overlap = set(m["production_companies"]) & seen_companies
                if not company_overlap:
                    diversity_boost *= 1.1
            # Boost para production companies diferentes (variedade de estúdios)
            if m.get("production_companies"):
                company_overlap = set(m["production_companies"]) & seen_companies
                if not company_overlap:
                    diversity_boost *= 1.1

            # Penalidade para gêneros muito repetidos
            genre_penalty = 1.0
            common_genres = set(m.get("genres", [])) & recommended_genres
            if len(common_genres) > 1:
                genre_penalty = 0.85
            elif len(common_genres) == 1:
                genre_penalty = 0.95

            adjusted_score = score * diversity_boost * genre_penalty

            diverse_recs.append((m, adjusted_score, score))
            if m.get("director"):
                seen_directors.add(m["director"])
            if m.get("production_companies"):
                seen_companies.update(m["production_companies"])
            recommended_genres.update(m.get("genres", []))

            if len(diverse_recs) >= k * 2:  # Pegar mais para ter margem
                break

        # Re-ordenar com scores ajustados
        diverse_recs.sort(key=lambda t: t[1], reverse=True)

        # Criar explicações ricas com dados TMDB
        out: List[Tuple[Dict, float, str]] = []
        for m, adjusted_score, original_score in diverse_recs[:k]:
            reason = self._build_reason(m, liked_ids)
            out.append((m, original_score, reason))
        return out

    def _build_reason(self, movie: Dict, liked_ids: List[int]) -> str:
        """Cria explicação rica usando dados TMDB"""
        midx = movie["id"] - 1
        liked_idx = [lid - 1 for lid in liked_ids if 1 <= lid <= len(self.movies)]
        if not liked_idx:
            return "✨ Recomendado por similaridade de conteúdo."

        sims = cosine_similarity(self._tfidf[midx], self._tfidf[liked_idx]).ravel()
        best_pos = int(sims.argmax())
        best_movie = self.movies[liked_idx[best_pos]]

        shared_genres = sorted(
            list(set(movie.get("genres", [])) & set(best_movie.get("genres", [])))
        )
        same_director = movie.get("director") == best_movie.get("director")

        # Keywords compartilhadas (muito importante!)
        shared_keywords = set(movie.get("keywords", [])) & set(
            best_movie.get("keywords", [])
        )

        # Elenco em comum
        shared_cast = set(movie.get("cast", [])[:5]) & set(
            best_movie.get("cast", [])[:5]
        )

        # Production companies em comum
        shared_companies = set(movie.get("production_companies", [])) & set(
            best_movie.get("production_companies", [])
        )

        parts = []

        # Título de referência
        parts.append(f"🎬 Baseado em '{best_movie['title']}'")

        # Razões específicas
        reasons = []
        if same_director:
            reasons.append(f"mesmo diretor ({movie.get('director')})")
        if shared_cast:
            actor = list(shared_cast)[0]
            reasons.append(f"atores em comum ({actor})")
        if shared_keywords and len(shared_keywords) >= 2:
            kws = list(shared_keywords)[:2]
            reasons.append(f"temas: {', '.join(kws)}")
        elif shared_keywords:
            kw = list(shared_keywords)[0]
            reasons.append(f"tema: {kw}")
        if shared_genres:
            reasons.append(f"{', '.join(shared_genres)}")
        if shared_companies:
            company = list(shared_companies)[0]
            reasons.append(f"estúdio: {company}")

        if reasons:
            parts.append(f" · {' | '.join(reasons[:3])}")  # Max 3 razões

        # Adicionar qualidade do filme
        if movie.get("vote_average") and movie.get("vote_count", 0) > 10:
            rating = movie["vote_average"]
            parts.append(f" · ⭐ {rating:.1f}/10")

        return "".join(parts)
