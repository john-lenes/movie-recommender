from typing import Dict, List, Set, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Constantes para pesos de features
WEIGHT_GENRES = 5
WEIGHT_KEYWORDS = 6
WEIGHT_DIRECTOR = 3
WEIGHT_CAST = 2
WEIGHT_CERTIFICATION = 2

# Constantes para limites e thresholds
MAX_OVERVIEW_WORDS = 150
MAX_CAST_MEMBERS = 5
MAX_COMPANIES = 3
MAX_COUNTRIES = 2
MIN_VOTES_FOR_QUALITY = 50
CURRENT_YEAR = 2026

# Constantes para boosts
BOOST_POPULARITY_SCALE = 40
BOOST_RATING_EXCELLENT = 1.3
BOOST_RATING_VERY_GOOD = 1.2
BOOST_RATING_GOOD = 1.15
BOOST_RATING_DECENT = 1.1
PENALTY_RATING_POOR = 0.8
BOOST_RECENT_MOVIES = 1.05
BOOST_MODERN_MOVIES = 1.02
BOOST_CLASSICS = 1.01
BOOST_COLLECTION = 1.1
BOOST_SAME_FRANCHISE = 1.3

# Constantes para diversidade
DIVERSITY_BOOST_NEW_DIRECTOR = 1.2
DIVERSITY_BOOST_NEW_COMPANY = 1.15
DIVERSITY_BOOST_SOME_OVERLAP = 1.05
DIVERSITY_BOOST_NEW_KEYWORDS = 1.1
DIVERSITY_PENALTY_KEYWORD_OVERLAP = 0.85
DIVERSITY_BOOST_NEW_DECADE = 1.08
GENRE_PENALTY_HIGH_OVERLAP = 0.8
GENRE_PENALTY_MEDIUM_OVERLAP = 0.9
GENRE_PENALTY_LOW_OVERLAP = 0.95

# Thresholds
RATING_THRESHOLD_EXCELLENT = 8.0
RATING_THRESHOLD_VERY_GOOD = 7.5
RATING_THRESHOLD_GOOD = 7.0
RATING_THRESHOLD_DECENT = 6.5
RATING_THRESHOLD_POOR = 5.0
AGE_RECENT = 3
AGE_MODERN = 10
AGE_CLASSIC = 40
KEYWORD_OVERLAP_LOW = 0.3
KEYWORD_OVERLAP_HIGH = 0.7


def _normalize_text(text: str) -> str:
    """Normaliza texto removendo pontos e convertendo para lowercase"""
    return text.strip().lower().replace(".", "")


def _extract_overview(movie: Dict) -> str:
    """Extrai e limita overview do filme"""
    overview = movie.get("overview", movie.get("description", ""))
    if overview:
        words = overview.lower().split()[:MAX_OVERVIEW_WORDS]
        return " ".join(words)
    return ""


def _repeat_text(text: str, weight: int) -> str:
    """Repete texto n vezes para amplificar importância no TF-IDF"""
    return " ".join([text] * weight)


def _movie_to_text(movie: Dict) -> str:
    """
    Converte filme em texto para análise de similaridade usando TF-IDF.
    Utiliza múltiplos fatores com pesos balanceados para recomendações precisas.
    """
    # Extrair características com pesos específicos
    genres = " ".join([g.strip().lower() for g in movie.get("genres", [])])
    director = _normalize_text(movie.get("director", ""))
    keywords = " ".join([k.strip().lower() for k in movie.get("keywords", [])])
    cast = " ".join([c.strip().lower() for c in movie.get("cast", [])[:MAX_CAST_MEMBERS]])
    companies = " ".join(
        [c.strip().lower() for c in movie.get("production_companies", [])[:MAX_COMPANIES]]
    )
    certification = _normalize_text(movie.get("certification") or "")
    decade = (movie.get("decade") or "").lower()
    original_language = (movie.get("original_language") or "").lower()
    countries = " ".join(
        [c.strip().lower() for c in movie.get("production_countries", [])[:MAX_COUNTRIES]]
    )
    overview_text = _extract_overview(movie)
    tagline = (movie.get("tagline") or "").lower()
    popularity_tier = (movie.get("popularity_tier") or "").lower()

    # Combinar com pesos estratégicos (repetindo para amplificar importância)
    parts = [
        f"generos:{_repeat_text(genres, WEIGHT_GENRES)}",
        f"keywords:{_repeat_text(keywords, WEIGHT_KEYWORDS)}",
        f"diretor:{_repeat_text(director, WEIGHT_DIRECTOR)}",
        f"elenco:{_repeat_text(cast, WEIGHT_CAST)}",
        f"empresas:{companies}",
        f"certificacao:{_repeat_text(certification, WEIGHT_CERTIFICATION)}",
        f"decada:{decade}",
        f"idioma:{original_language}",
        f"paises:{countries}",
        f"popularidade:{popularity_tier}",
        f"tagline:{tagline}",
        f"sinopse:{overview_text}",
    ]

    return " ".join(parts)


class ContentBasedRecommender:
    """
    Sistema de recomendação baseado em conteúdo usando TF-IDF e similaridade de cosseno.
    Analisa características dos filmes para sugerir títulos similares aos gostos do usuário.
    """

    def __init__(self, movies: List[Dict]):
        self.movies = movies
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
            return self._get_cold_start_recommendations(candidates, k)ularity:
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
        self._apply_dislike_penalty(sims, disliked_ids)

        # Aplicar boosts de popularidade, qualidade e contexto temporal
        self._apply_boosts(sims# Boost para diretores ainda não vistos (diversidade)
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
                seen_coself._apply_diversity_reranking(ranked, liked_ids, k

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
                parts.appendetalhada usando características compartilhadas com filmes curtidos"""
        midx = self._id_to_idx[movie["id"]]
        liked_idx = [self._id_to_idx[lid] for lid in liked_ids if lid in self._id_to_idx]
        
        if not liked_idx:
            return "✨ Recomendado por similaridade de conteúdo."

        # Encontrar filme curtido mais similar
        sims = cosine_similarity(self._tfidf[midx], self._tfidf[liked_idx]).ravel()
        best_movie = self.movies[liked_idx[int(sims.argmax())]]

        # Analisar características compartilhadas
        shared_features = self._analyze_shared_features(movie, best_movie)
        
        # Construir explicação
        parts = [f"🎬 Baseado em '{best_movie['title']}'"]
        
        # Adicionar razões priorizadas
        if reasons := self._build_reason_list(movie, shared_features):
            parts.append(f" · {' | '.join(reasons[:4])}")

        # Adicionar qualidade do filme
        if quality_info := self._format_quality_info(movie):
            parts.append(f" · {quality_info}")

        return "".join(parts)

    def _analyze_shared_features(self, movie: Dict, reference: Dict) -> Dict:
        """Analisa características compartilhadas entre dois filmes"""
        return {
            "genres": sorted(set(movie.get("genres", [])) & set(reference.get("genres", []))),
            "same_director": movie.get("director") == reference.get("director") and movie.get("director"),
            "keywords": set(movie.get("keywords", [])) & set(reference.get("keywords", [])),
            "cast": set(movie.get("cast", [])[:5]) & set(reference.get("cast", [])[:5]),
            "companies": set(movie.get("production_companies", [])) & set(reference.get("production_companies", [])),
            "same_certification": (
                movie.get("certification") and reference.get("certification") 
                and movie["certification"] == reference["certification"]
            ),
            "same_decade": (
                movie.get("decade") and reference.get("decade") 
                and movie["decade"] == reference["decade"]
            ),
            "same_collection": (
                movie.get("belongs_to_collection") and reference.get("belongs_to_collection")
                and movie["belongs_to_collection"]["id"] == reference["belongs_to_collection"]["id"]
            ),
        }

    def _build_reason_list(self, movie: Dict, features: Dict) -> List[str]:
        """Constrói lista de razões priorizadas para a recomendação"""
        reasons = []

        # Prioridade 1: Mesma franquia
        if features["same_collection"]:
            reasons.append(f"mesma franquia ({movie['belongs_to_collection']['name']})")

        # Prioridade 2: Mesmo diretor
        if features["same_director"]:
            reasons.append(f"diretor: {movie['director']}")

        # Prioridade 3: Keywords compartilhadas
        if features["keywords"]:
            kw_count = len(features["keywords"])
            if kw_count >= 3:
                reasons.append(f"temas: {', '.join(list(features['keywords'])[:3])}")
            elif kw_count >= 2:
                reasons.append(f"temas: {', '.join(list(features['keywords'])[:2])}")
            else:
                reasons.append(f"tema: {list(features['keywords'])[0]}")

        # Prioridade 4: Elenco em comum
        if features["cast"]:
            cast_count = len(features["cast"])
            if cast_count >= 2:
                reasons.append(f"elenco: {', '.join(list(features['cast'])[:2])}")
            else:
                reasons.append(f"ator: {list(features['cast'])[0]}")

        # Prioridade 5: Gêneros
        if features["genres"]:
            if len(features["genres"]) >= 2:
                reasons.append(f"gêneros: {', '.join(features['genres'][:2])}")
            else:
                reasons.append(f"gênero: {features['genres'][0]}")

        # Prioridade 6: Mesma certificação
        if features["same_certification"]:
            reasons.append(f"classificação: {movie['certification']}")

        # Prioridade 7: Mesma década
        if features["same_decade"]:
            reasons.append(f"época: {movie['decade']}")

        # Prioridade 8: Estúdio
        if features["companies"]:
            reasons.append(f"estúdio: {list(features['companies'])[0]}")

        return reasons

    def _format_quality_info(self, movie: Dict) -> str:
        """Formata informações de qualidade do filme"""
        if not (rating := movie.get("vote_average")):
            return ""
        if movie.get("vote_count", 0) <= MIN_VOTES_FOR_QUALITY:
            return ""

        vote_count = movie["vote_count"]
        if rating >= RATING_THRESHOLD_EXCELLENT:
            return f"⭐ {rating:.1f}/10 ({vote_count} votos)"
        elif rating >= RATING_THRESHOLD_GOOD:
            return f"⭐ {rating:.1f}/10"
        return ""lty(
        self, movie: Dict, recommended_genres: Set[str]
    ) -> float:
        """Calcula penalidade para gêneros muito repetidos"""
        common_genres = set(movie.get("genres", [])) & recommended_genres
        if len(common_genres) > 2:
            return GENRE_PENALTY_HIGH_OVERLAP
        elif len(common_genres) == 2:
            return GENRE_PENALTY_MEDIUM_OVERLAP
        elif len(common_genres) == 1:
            return GENRE_PENALTY_LOW_OVERLAP
        return 1.0

    def _calculate_franchise_boost(self, movie: Dict, liked_ids: List[int]) -> float:
        """Calcula boost para filmes da mesma franquia dos curtidos"""
        if not (collection := movie.get("belongs_to_collection")):
            return 1.0

        for lid in liked_ids:
            if liked_movie := next((m for m in self.movies if m["id"] == lid), None):
                if liked_collection := liked_movie.get("belongs_to_collection"):
                    if collection["id"] == liked_collection["id"]:
                        return BOOST_SAME_FRANCHISE
        return 1.0

    def _apply_diversity_reranking(
        self, ranked: List[Tuple[Dict, float]], liked_ids: List[int], k: int
    ) -> List[Tuple[Dict, float, float]]:
        """Aplica re-ranking para garantir diversidade nas recomendações"""
        diverse_recs = []
        seen_directors: Set[str] = set()
        seen_companies: Set[str] = set()
        recommended_genres: Set[str] = set()
        seen_keywords: Set[str] = set()
        seen_decades: Set[str] = set()

        for m, score in ranked:
            diversity_boost = self._calculate_diversity_boost(
                m, seen_directors, seen_companies, seen_keywords, seen_decades
            )
            genre_penalty = self._calculate_genre_penalty(m, recommended_genres)
            franchise_boost = self._calculate_franchise_boost(m, liked_ids)

            adjusted_score = score * diversity_boost * genre_penalty * franchise_boost
            diverse_recs.append((m, adjusted_score, score))

            # Atualizar conjuntos vistos
            if director := m.get("director"):
                seen_directors.add(director)
            if companies := m.get("production_companies"):
                seen_companies.update(companies[:2])
            if keywords := m.get("keywords"):
                seen_keywords.update(keywords[:5])
            if decade := m.get("decade"):
                seen_decades.add(decade)
            recommended_genres.update(m.get("genres", []))

            if len(diverse_recs) >= k * 3:
                break

        diverse_recs.sort(key=lambda t: t[1], reverse=True)
        return diverse_recs