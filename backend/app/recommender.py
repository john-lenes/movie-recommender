from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _movie_to_text(movie: Dict) -> str:
    """
    Conteúdo usado para similaridade: algoritmo melhorado com características precisas
    Utiliza múltiplos fatores com pesos balanceados para recomendações mais assertivas
    """
    # Gêneros (peso muito alto - fundamental para similaridade)
    genres = " ".join([g.strip().lower() for g in movie.get("genres", [])])

    # Diretor (peso alto - estilo único de cada diretor)
    director = movie.get("director", "").strip().lower().replace(".", "")

    # Keywords do TMDB (peso altíssimo - características mais precisas)
    keywords = " ".join([k.strip().lower() for k in movie.get("keywords", [])])

    # Elenco principal (top 5 atores mais relevantes)
    cast = " ".join([c.strip().lower() for c in movie.get("cast", [])[:5]])

    # Production companies (estúdios tem identidade visual e temática)
    companies = " ".join(
        [c.strip().lower() for c in movie.get("production_companies", [])[:3]]
    )

    # Certification/Classificação (público-alvo similar)
    certification = (movie.get("certification") or "").lower().replace("-", "")

    # Década (contexto temporal e estilo)
    decade = (movie.get("decade") or "").lower()

    # Idioma original (indica tipo de produção)
    original_language = (movie.get("original_language") or "").lower()

    # Países de produção (estilo regional)
    countries = " ".join(
        [c.strip().lower() for c in movie.get("production_countries", [])[:2]]
    )

    # Overview/descrição (primeiras 150 palavras - reduzido para não dominar)
    overview = movie.get("overview", movie.get("description", ""))
    if overview:
        words = overview.lower().split()[:150]
        overview_text = " ".join(words)
    else:
        overview_text = ""

    # Tagline (frases de efeito são muito descritivas)
    tagline = (movie.get("tagline") or "").lower()

    # Tier de popularidade (contexto de alcance)
    popularity_tier = (movie.get("popularity_tier") or "").lower()

    # Combinar tudo com pesos estratégicos (repetindo para amplificar importância)
    parts = [
        f"generos:{genres} {genres} {genres} {genres} {genres}",  # Peso 5x - Essencial
        f"keywords:{keywords} {keywords} {keywords} {keywords} {keywords} {keywords}",  # Peso 6x - Mais preciso
        f"diretor:{director} {director} {director}",  # Peso 3x - Estilo único
        f"elenco:{cast} {cast}",  # Peso 2x - Atores reconhecíveis
        f"empresas:{companies}",  # Peso 1x
        f"certificacao:{certification} {certification}",  # Peso 2x - Público-alvo
        f"decada:{decade}",  # Peso 1x
        f"idioma:{original_language}",  # Peso 1x
        f"paises:{countries}",  # Peso 1x
        f"popularidade:{popularity_tier}",  # Peso 1x
        f"tagline:{tagline}",  # Peso 1x
        f"sinopse:{overview_text}",  # Peso 1x
    ]

    return " ".join(parts)


class ContentBasedRecommender:
    def __init__(self, movies: List[Dict]):
        self.movies = movies
        # Criar mapa de ID do filme para índice na lista (necessário porque IDs não são sequenciais)
        self._id_to_idx = {m["id"]: idx for idx, m in enumerate(movies)}
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
        liked_idx = [
            self._id_to_idx[lid] for lid in liked_ids if lid in self._id_to_idx
        ]
        if not liked_idx:
            return []

        user_vec = self._tfidf[liked_idx].mean(axis=0)
        # Converter para array se for matrix (compatibilidade com versões do sklearn)
        if hasattr(user_vec, "A"):
            user_vec = user_vec.A

        # Calcular similaridade com todos os filmes
        sims = cosine_similarity(user_vec, self._tfidf).ravel()

        # Penalizar filmes não curtidos mais fortemente
        for did in disliked_ids:
            if did in self._id_to_idx:
                sims[self._id_to_idx[did]] *= 0.1

        # Aplicar boost de popularidade, qualidade e contexto temporal
        for idx, m in enumerate(self.movies):
            # Boost de popularidade (log scale para não dominar)
            popularity_boost = 1.0
            if m.get("popularity"):
                popularity_boost = 1.0 + (np.log1p(m["popularity"]) / 40)

            # Boost de qualidade (rating com votos suficientes)
            quality_boost = 1.0
            if m.get("vote_average") and m.get("vote_count", 0) > 50:
                # Filmes muito bem avaliados merecem boost maior
                rating = m["vote_average"]
                if rating >= 8.0:
                    quality_boost = 1.3
                elif rating >= 7.5:
                    quality_boost = 1.2
                elif rating >= 7.0:
                    quality_boost = 1.15
                elif rating >= 6.5:
                    quality_boost = 1.1
                elif rating < 5.0:
                    quality_boost = 0.8  # Penalidade para filmes mal avaliados

            # Boost temporal: filmes muito antigos ou muito recentes podem ter boost
            year_boost = 1.0
            if m.get("year"):
                year = m["year"]
                current_year = 2026
                age = current_year - year
                if age <= 3:  # Filmes muito recentes
                    year_boost = 1.05
                elif age <= 10:  # Filmes modernos
                    year_boost = 1.02
                elif age > 40:  # Clássicos podem ser valorizados
                    year_boost = 1.01

            # Boost para filmes de coleções/franquias (tendem a ser apreciados por fãs)
            collection_boost = 1.0
            if m.get("belongs_to_collection"):
                collection_boost = 1.1

            # Aplicar todos os boosts
            sims[idx] *= (
                popularity_boost * quality_boost * year_boost * collection_boost
            )

        # Ranquear candidatos
        ranked = sorted(
            ((m, float(sims[self._id_to_idx[m["id"]]])) for m in candidates),
            key=lambda t: t[1],
            reverse=True,
        )

        # Aplicar re-ranking para diversidade e relevância
        diverse_recs = []
        seen_directors = set()
        seen_companies = set()
        recommended_genres = set()
        seen_keywords = set()  # Evitar keywords muito repetidas
        seen_decades = set()  # Diversidade temporal

        for m, score in ranked:
            # Boost para diretores ainda não vistos (diversidade)
            diversity_boost = 1.0
            if m.get("director") and m["director"] not in seen_directors:
                diversity_boost *= 1.2

            # Boost para production companies diferentes
            if m.get("production_companies"):
                company_overlap = set(m["production_companies"]) & seen_companies
                if not company_overlap:
                    diversity_boost *= 1.15
                elif len(company_overlap) < len(seen_companies) / 2:
                    diversity_boost *= 1.05

            # Boost para keywords novas (evitar repetição temática)
            if m.get("keywords"):
                keyword_overlap = set(m["keywords"][:5]) & seen_keywords
                overlap_ratio = len(keyword_overlap) / max(len(m["keywords"][:5]), 1)
                if overlap_ratio < 0.3:  # Menos de 30% de overlap
                    diversity_boost *= 1.1
                elif overlap_ratio > 0.7:  # Mais de 70% de overlap
                    diversity_boost *= 0.85

            # Boost para décadas diferentes (variedade temporal)
            if m.get("decade") and m["decade"] not in seen_decades:
                diversity_boost *= 1.08

            # Penalidade para gêneros muito repetidos
            genre_penalty = 1.0
            common_genres = set(m.get("genres", [])) & recommended_genres
            if len(common_genres) > 2:  # Mais de 2 gêneros em comum
                genre_penalty = 0.8
            elif len(common_genres) == 2:
                genre_penalty = 0.9
            elif len(common_genres) == 1:
                genre_penalty = 0.95

            # Boost para filmes de coleções relacionadas aos filmes curtidos
            collection_boost = 1.0
            if m.get("belongs_to_collection"):
                for lid in liked_ids:
                    liked_movie = next(
                        (lm for lm in self.movies if lm["id"] == lid), None
                    )
                    if liked_movie and liked_movie.get("belongs_to_collection"):
                        if (
                            m["belongs_to_collection"]["id"]
                            == liked_movie["belongs_to_collection"]["id"]
                        ):
                            collection_boost = 1.3  # Mesma franquia - boost forte
                            break

            adjusted_score = score * diversity_boost * genre_penalty * collection_boost

            diverse_recs.append((m, adjusted_score, score))

            # Atualizar conjuntos vistos
            if m.get("director"):
                seen_directors.add(m["director"])
            if m.get("production_companies"):
                seen_companies.update(m["production_companies"][:2])
            if m.get("keywords"):
                seen_keywords.update(m["keywords"][:5])
            if m.get("decade"):
                seen_decades.add(m["decade"])
            recommended_genres.update(m.get("genres", []))

            if (
                len(diverse_recs) >= k * 3
            ):  # Pegar 3x mais para ter boa margem de escolha
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
        """Cria explicação rica e precisa usando características dos filmes curtidos"""
        midx = self._id_to_idx[movie["id"]]
        liked_idx = [
            self._id_to_idx[lid] for lid in liked_ids if lid in self._id_to_idx
        ]
        if not liked_idx:
            return "✨ Recomendado por similaridade de conteúdo."

        sims = cosine_similarity(self._tfidf[midx], self._tfidf[liked_idx]).ravel()
        best_pos = int(sims.argmax())
        best_movie = self.movies[liked_idx[best_pos]]

        # Analisar características compartilhadas com precisão
        shared_genres = sorted(
            list(set(movie.get("genres", [])) & set(best_movie.get("genres", [])))
        )
        same_director = movie.get("director") == best_movie.get(
            "director"
        ) and movie.get("director")

        # Keywords compartilhadas (mais preciso)
        shared_keywords = set(movie.get("keywords", [])) & set(
            best_movie.get("keywords", [])
        )

        # Elenco em comum (top 5 atores principais)
        shared_cast = set(movie.get("cast", [])[:5]) & set(
            best_movie.get("cast", [])[:5]
        )

        # Production companies em comum
        shared_companies = set(movie.get("production_companies", [])) & set(
            best_movie.get("production_companies", [])
        )

        # Certificação similar (mesmo público-alvo)
        same_certification = (
            movie.get("certification")
            and best_movie.get("certification")
            and movie["certification"] == best_movie["certification"]
        )

        # Mesma década
        same_decade = (
            movie.get("decade")
            and best_movie.get("decade")
            and movie["decade"] == best_movie["decade"]
        )

        # Mesma coleção/franquia
        same_collection = (
            movie.get("belongs_to_collection")
            and best_movie.get("belongs_to_collection")
            and movie["belongs_to_collection"]["id"]
            == best_movie["belongs_to_collection"]["id"]
        )

        parts = []

        # Título de referência
        parts.append(f"🎬 Baseado em '{best_movie['title']}'")

        # Razões específicas e priorizadas
        reasons = []

        # Prioridade 1: Mesma franquia
        if same_collection:
            reasons.append(f"mesma franquia ({movie['belongs_to_collection']['name']})")

        # Prioridade 2: Mesmo diretor
        if same_director:
            reasons.append(f"diretor: {movie['director']}")

        # Prioridade 3: Keywords (temas) compartilhadas
        if shared_keywords:
            if len(shared_keywords) >= 3:
                kws = list(shared_keywords)[:3]
                reasons.append(f"temas: {', '.join(kws)}")
            elif len(shared_keywords) >= 2:
                kws = list(shared_keywords)[:2]
                reasons.append(f"temas: {', '.join(kws)}")
            else:
                kw = list(shared_keywords)[0]
                reasons.append(f"tema: {kw}")

        # Prioridade 4: Elenco em comum
        if shared_cast:
            if len(shared_cast) >= 2:
                actors = list(shared_cast)[:2]
                reasons.append(f"elenco: {', '.join(actors)}")
            else:
                actor = list(shared_cast)[0]
                reasons.append(f"ator: {actor}")

        # Prioridade 5: Gêneros
        if shared_genres:
            if len(shared_genres) >= 2:
                reasons.append(f"gêneros: {', '.join(shared_genres[:2])}")
            else:
                reasons.append(f"gênero: {shared_genres[0]}")

        # Prioridade 6: Mesma certificação
        if same_certification:
            reasons.append(f"classificação: {movie['certification']}")

        # Prioridade 7: Mesma década
        if same_decade:
            reasons.append(f"época: {movie['decade']}")

        # Prioridade 8: Estúdio
        if shared_companies:
            company = list(shared_companies)[0]
            reasons.append(f"estúdio: {company}")

        # Montar explicação (máximo 4 razões para não ficar verboso)
        if reasons:
            parts.append(f" · {' | '.join(reasons[:4])}")

        # Adicionar qualidade do filme
        if movie.get("vote_average") and movie.get("vote_count", 0) > 50:
            rating = movie["vote_average"]
            vote_count = movie["vote_count"]
            if rating >= 8.0:
                parts.append(f" · ⭐ {rating:.1f}/10 ({vote_count} votos)")
            elif rating >= 7.0:
                parts.append(f" · ⭐ {rating:.1f}/10")

        return "".join(parts)
