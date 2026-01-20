import { memo, useEffect, useMemo, useState } from "react";
import {
  getAuthToken,
  getMe,
  getMovies,
  getRecommendations,
  logout,
  rateMovie,
  sendFeedback,
  type Movie,
  type Recommendation,
  type User,
} from "./api";
import AuthModal from "./AuthModal";
import { Toaster, toast } from "./components/Toaster";
import { usePagination } from "./hooks/usePagination";

const Badge = memo(function Badge({
  children,
  variant = "default",
}: {
  children: string;
  variant?: "default" | "neutral";
}) {
  const baseClasses =
    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border";
  const variantClasses =
    variant === "neutral"
      ? "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700"
      : "bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300 border-primary-200 dark:border-primary-800";

  return <span className={`${baseClasses} ${variantClasses}`}>{children}</span>;
});

const StarRating = memo(function StarRating({
  rating,
  onRate,
}: {
  rating: number;
  onRate?: (stars: number) => void;
}) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`text-xl cursor-pointer transition-all duration-200 ${
            star <= rating
              ? "text-yellow-400 scale-110"
              : "text-gray-300 dark:text-gray-600 hover:text-yellow-300 hover:scale-105"
          }`}
          onClick={() => onRate && onRate(star)}
          style={{ cursor: onRate ? "pointer" : "default" }}
        >
          ★
        </span>
      ))}
    </div>
  );
});

interface MovieCardProps {
  movie: Movie;
  userRating: number;
  isLiked: boolean;
  isDisliked: boolean;
  onRate: (stars: number) => void;
  onVote: (action: "like" | "dislike") => void;
}

const MovieCard = memo(function MovieCard({
  movie: m,
  userRating,
  isLiked,
  isDisliked,
  onRate,
  onVote,
}: MovieCardProps) {
  const [isImageExpanded, setIsImageExpanded] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const posterUrl = m.poster_path
    ? `https://image.tmdb.org/t/p/w500${m.poster_path}`
    : null;

  return (
    <div
      className="glass rounded-xl p-4 space-y-3 transition-all duration-300 shadow-lg hover:shadow-2xl flex flex-col group relative overflow-hidden"
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      <div className="flex items-start gap-3">
        {posterUrl && (
          <img
            src={posterUrl}
            alt={m.title}
            loading="lazy"
            className={`object-cover rounded-lg shadow-md flex-shrink-0 cursor-pointer transition-all duration-300 ${
              isImageExpanded ? "w-40 h-56" : "w-20 h-28"
            }`}
            onMouseEnter={() => setIsImageExpanded(true)}
            onMouseLeave={() => setIsImageExpanded(false)}
          />
        )}
        <div className="flex-1 min-w-0">
          {m.original_title && m.original_title !== m.title ? (
            <>
              <h3 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
                {m.original_title}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 italic">
                {m.title}
              </p>
            </>
          ) : (
            <h3 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
              {m.title}
            </h3>
          )}
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {m.year}
            </span>
            {m.runtime && (
              <span className="text-sm text-gray-600 dark:text-gray-400">
                • {m.runtime} min
              </span>
            )}
            {m.vote_average && (
              <div className="flex items-center gap-1">
                <span className="text-yellow-400">★</span>
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {m.vote_average.toFixed(1)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="text-sm text-gray-700 dark:text-gray-300">
        <span className="font-medium text-gray-600 dark:text-gray-400">
          Diretor:
        </span>{" "}
        {m.director}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {m.genres.map((g) => (
          <Badge key={g} variant="neutral">
            {g}
          </Badge>
        ))}
      </div>

      {/* Sinopse fixa */}
      <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
          Sinopse:
        </p>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          {m.description}
        </p>
      </div>

      {/* Informações expansíveis */}
      <div
        className={`transition-all duration-300 overflow-hidden ${
          isExpanded ? "max-h-[1200px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        {/* Tagline */}
        {m.tagline && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm italic text-primary-600 dark:text-primary-400">
              "{m.tagline}"
            </p>
          </div>
        )}

        {/* Métricas principais */}
        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-2">
            {m.score_composite && (
              <div className="bg-green-100 dark:bg-green-900/30 rounded-lg p-2">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Score Composto
                </p>
                <p className="text-lg font-bold text-green-700 dark:text-green-400">
                  {m.score_composite.toFixed(1)}/10
                </p>
              </div>
            )}

            {m.popularity_tier && (
              <div
                className={`rounded-lg p-2 ${
                  m.popularity_tier === "Viral"
                    ? "bg-red-100 dark:bg-red-900/30"
                    : m.popularity_tier === "High"
                      ? "bg-orange-100 dark:bg-orange-900/30"
                      : m.popularity_tier === "Medium"
                        ? "bg-blue-100 dark:bg-blue-900/30"
                        : "bg-gray-100 dark:bg-gray-800"
                }`}
              >
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Popularidade
                </p>
                <p
                  className={`text-lg font-bold ${
                    m.popularity_tier === "Viral"
                      ? "text-red-700 dark:text-red-400"
                      : m.popularity_tier === "High"
                        ? "text-orange-700 dark:text-orange-400"
                        : m.popularity_tier === "Medium"
                          ? "text-blue-700 dark:text-blue-400"
                          : "text-gray-700 dark:text-gray-400"
                  }`}
                >
                  {m.popularity_tier}
                </p>
              </div>
            )}

            {m.certification && (
              <div className="bg-purple-100 dark:bg-purple-900/30 rounded-lg p-2">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Classificação
                </p>
                <p className="text-lg font-bold text-purple-700 dark:text-purple-400">
                  {m.certification}
                </p>
              </div>
            )}

            {m.trending_score && (
              <div className="bg-yellow-100 dark:bg-yellow-900/30 rounded-lg p-2">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Trending
                </p>
                <p className="text-lg font-bold text-yellow-700 dark:text-yellow-400">
                  {m.trending_score.toFixed(1)}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Dados financeiros */}
        {(m.budget || m.revenue || m.roi !== undefined) && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
              💰 Finanças
            </p>
            <div className="grid grid-cols-3 gap-2 text-xs">
              {m.budget && (
                <div>
                  <p className="text-gray-500 dark:text-gray-500">Orçamento</p>
                  <p className="font-semibold text-gray-700 dark:text-gray-300">
                    ${(m.budget / 1_000_000).toFixed(1)}M
                  </p>
                </div>
              )}
              {m.revenue && (
                <div>
                  <p className="text-gray-500 dark:text-gray-500">Receita</p>
                  <p className="font-semibold text-gray-700 dark:text-gray-300">
                    ${(m.revenue / 1_000_000).toFixed(1)}M
                  </p>
                </div>
              )}
              {m.roi !== undefined && m.roi !== null && (
                <div>
                  <p className="text-gray-500 dark:text-gray-500">ROI</p>
                  <p
                    className={`font-bold ${m.roi > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
                  >
                    {m.roi > 0 ? "+" : ""}
                    {m.roi}%
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Coleção/Franquia */}
        {m.belongs_to_collection && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              📚 Franquia
            </p>
            <div className="flex items-center gap-2 bg-gradient-to-r from-primary-100 to-primary-50 dark:from-primary-900/30 dark:to-primary-800/20 rounded-lg p-2">
              {m.belongs_to_collection.poster_path && (
                <img
                  src={`https://image.tmdb.org/t/p/w92${m.belongs_to_collection.poster_path}`}
                  alt={m.belongs_to_collection.name}
                  className="w-10 h-14 object-cover rounded shadow-sm"
                />
              )}
              <p className="text-sm font-medium text-primary-700 dark:text-primary-300">
                {m.belongs_to_collection.name}
              </p>
            </div>
          </div>
        )}

        {/* Elenco */}
        {m.cast && m.cast.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              🎭 Elenco principal
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {m.cast.slice(0, 5).join(", ")}
              {m.cast.length > 5 && ` (+${m.cast.length - 5} mais)`}
            </p>
          </div>
        )}

        {/* Production Companies */}
        {m.production_companies && m.production_companies.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              🏢 Estúdios
            </p>
            <div className="flex flex-wrap gap-1">
              {m.production_companies.map((company, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full"
                >
                  {company}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Keywords */}
        {m.keywords && m.keywords.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              🏷️ Keywords
            </p>
            <div className="flex flex-wrap gap-1">
              {m.keywords.slice(0, 10).map((kw, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                >
                  {kw}
                </span>
              ))}
              {m.keywords.length > 10 && (
                <span className="text-xs text-gray-500 dark:text-gray-500">
                  +{m.keywords.length - 10} mais
                </span>
              )}
            </div>
          </div>
        )}

        {/* Idiomas */}
        {m.spoken_languages && m.spoken_languages.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              🗣️ Idiomas
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {m.spoken_languages.map((l) => l.name).join(", ")}
            </p>
          </div>
        )}

        {/* Rating Stats (MovieLens) */}
        {m.rating_stats && m.rating_stats.average && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              📊 Stats MovieLens
            </p>
            <div className="grid grid-cols-4 gap-2 text-xs">
              <div>
                <p className="text-gray-500 dark:text-gray-500">Média</p>
                <p className="font-semibold text-gray-700 dark:text-gray-300">
                  {m.rating_stats.average.toFixed(2)}/5
                </p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-500">Votos</p>
                <p className="font-semibold text-gray-700 dark:text-gray-300">
                  {m.rating_stats.count}
                </p>
              </div>
              {m.rating_stats.min !== undefined && (
                <div>
                  <p className="text-gray-500 dark:text-gray-500">Min</p>
                  <p className="font-semibold text-gray-700 dark:text-gray-300">
                    {m.rating_stats.min}
                  </p>
                </div>
              )}
              {m.rating_stats.max !== undefined && (
                <div>
                  <p className="text-gray-500 dark:text-gray-500">Max</p>
                  <p className="font-semibold text-gray-700 dark:text-gray-300">
                    {m.rating_stats.max}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Links externos */}
        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
          <div className="flex gap-2">
            {m.imdb_id && (
              <a
                href={`https://www.imdb.com/title/${m.imdb_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs px-3 py-1 bg-yellow-500 text-white rounded-full hover:bg-yellow-600 transition-colors font-medium"
              >
                IMDb
              </a>
            )}
            {m.tmdb_id && (
              <a
                href={`https://www.themoviedb.org/movie/${m.tmdb_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs px-3 py-1 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors font-medium"
              >
                TMDB
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-2 pt-2 border-t border-gray-200 dark:border-gray-700">
        <StarRating rating={userRating} onRate={onRate} />

        <div className="flex gap-2">
          <button
            onClick={() => onVote("like")}
            className={`flex-1 py-2 rounded-lg text-center transition-all duration-200 font-medium ${
              isLiked
                ? "bg-gradient-to-r from-gray-600 to-gray-700 text-white shadow-lg"
                : "glass hover:scale-105"
            }`}
          >
            👍
          </button>
          <button
            onClick={() => onVote("dislike")}
            className={`flex-1 py-2 rounded-lg text-center transition-all duration-200 font-medium ${
              isDisliked
                ? "bg-gray-600 text-white shadow-lg"
                : "glass hover:scale-105"
            }`}
          >
            👎
          </button>
        </div>
      </div>
    </div>
  );
});

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [selectedGenres, setSelectedGenres] = useState<Set<string>>(new Set());
  const [yearRange, setYearRange] = useState<[number, number]>([1990, 2025]);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [sortBy, setSortBy] = useState<"year" | "title" | "rating">("year");

  // Carregar preferências do localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) setTheme(savedTheme as "dark" | "light");
  }, []);

  // Salvar tema
  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  // Verificar autenticação ao carregar
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await getMovies();
        setMovies(data);

        // Tentar autenticar com token existente
        const token = getAuthToken();
        if (token) {
          try {
            const userData = await getMe();
            setUser(userData);

            // Carregar recomendações se tem interações
            if (
              userData.liked_movies.length > 0 ||
              userData.disliked_movies.length > 0
            ) {
              const rr = await getRecommendations(10);
              setRecs(rr.recommendations);
            }
          } catch (authError) {
            // Token inválido, limpar
          }
        }
      } catch (e: any) {
        setError(e?.message ?? "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const allGenres = useMemo(() => {
    const genres = new Set<string>();
    movies.forEach((m) => m.genres.forEach((g) => genres.add(g)));
    return Array.from(genres).sort();
  }, [movies]);

  const yearBounds = useMemo(() => {
    if (movies.length === 0) return { min: 1990, max: 2025 };
    const years = movies.map((m) => m.year);
    return {
      min: Math.min(...years),
      max: Math.max(...years),
    };
  }, [movies]);

  // Ajustar yearRange quando os filmes carregarem
  useEffect(() => {
    if (movies.length > 0) {
      setYearRange([yearBounds.min, yearBounds.max]);
    }
  }, [movies.length, yearBounds]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let result = movies.filter((m) => {
      const matchesQuery =
        !q ||
        [m.title, m.director, m.genres.join(" "), String(m.year)].some((x) =>
          x.toLowerCase().includes(q),
        );
      const matchesGenres =
        selectedGenres.size === 0 ||
        m.genres.some((g) => selectedGenres.has(g));
      const matchesYear = m.year >= yearRange[0] && m.year <= yearRange[1];
      return matchesQuery && matchesGenres && matchesYear;
    });

    // Ordenar
    if (sortBy === "year") {
      result.sort((a, b) => b.year - a.year);
    } else if (sortBy === "title") {
      result.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortBy === "rating") {
      const userRatings = user?.ratings || {};
      result.sort(
        (a, b) => (userRatings[b.id] || 0) - (userRatings[a.id] || 0),
      );
    }

    return result;
  }, [movies, query, selectedGenres, yearRange, sortBy, user]);

  const pagination = usePagination(filtered, 20);

  const stats = useMemo(() => {
    if (!user) return { totalRatings: 0, avgRating: 0 };

    const ratingsArray = Object.values(user.ratings);
    const totalRatings = ratingsArray.length;
    const avgRating =
      totalRatings > 0
        ? ratingsArray.reduce((sum, r) => sum + r, 0) / totalRatings
        : 0;
    return { totalRatings, avgRating };
  }, [user]);

  async function onVote(movieId: number, action: "like" | "dislike") {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    try {
      setError(null);
      const response = await sendFeedback(movieId, action);
      setUser(response.user);

      // Atualizar recomendações
      const rr = await getRecommendations(10);
      setRecs(rr.recommendations);

      toast.success(
        action === "like" ? "Filme curtido!" : "Feedback registrado!",
      );
    } catch (e: any) {
      const errorMsg = e?.message ?? "Erro ao votar";
      setError(errorMsg);
      toast.error(errorMsg);
    }
  }

  async function handleRate(movieId: number, stars: number) {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    try {
      const response = await rateMovie(movieId, stars);
      setUser(response.user);
      toast.success(`Avaliado com ${stars} estrela${stars > 1 ? "s" : ""}!`);
    } catch (e: any) {
      const errorMsg = e?.message ?? "Erro ao avaliar";
      setError(errorMsg);
      toast.error(errorMsg);
    }
  }

  async function handleLogout() {
    await logout();
    setUser(null);
    setRecs([]);
    toast.info("Você saiu da conta");
    setShowAuthModal(true);
  }

  async function handleAuthSuccess() {
    setShowAuthModal(false);
    try {
      const userData = await getMe();
      setUser(userData);

      // Carregar recomendações se tem interações
      if (
        userData.liked_movies.length > 0 ||
        userData.disliked_movies.length > 0
      ) {
        const rr = await getRecommendations(10);
        setRecs(rr.recommendations);
      }
    } catch (e: any) {
      setError(e?.message ?? "Erro ao carregar dados");
    }
  }

  function toggleGenre(genre: string) {
    const next = new Set(selectedGenres);
    if (next.has(genre)) {
      next.delete(genre);
    } else {
      next.add(genre);
    }
    setSelectedGenres(next);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-gray-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-700 to-gray-900 dark:from-gray-300 dark:to-gray-100 bg-clip-text text-transparent">
            🎬 Recomendador de Filmes
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Carregando dados do TMDB...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Toaster />
      {showAuthModal && (
        <AuthModal
          onSuccess={handleAuthSuccess}
          onClose={() => setShowAuthModal(false)}
        />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12 space-y-6 sm:space-y-8">
        {/* Header */}
        <header className="glass-strong rounded-2xl p-4 sm:p-6 lg:p-8 shadow-xl animate-fade-in">
          <div className="flex flex-col lg:flex-row gap-4 lg:gap-6 lg:items-start lg:justify-between">
            <div className="space-y-2">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-gray-700 via-gray-800 to-gray-900 dark:from-gray-300 dark:via-gray-200 dark:to-gray-100 bg-clip-text text-transparent">
                🎬 Recomendador de Filmes
              </h1>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                {user
                  ? `Olá, ${user.username}! Sistema inteligente com dados do TMDB`
                  : "Sistema inteligente com dados do TMDB"}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 sm:gap-4">
              {/* Theme Toggle */}
              <button
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="p-3 rounded-xl glass hover:scale-110 transition-transform duration-200 shadow-lg"
                aria-label="Alternar tema"
              >
                <span className="text-2xl">
                  {theme === "dark" ? "☀️" : "🌙"}
                </span>
              </button>

              {/* User info */}
              {user ? (
                <>
                  <div className="flex flex-wrap gap-2 sm:gap-3">
                    <div className="glass rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-center min-w-[70px] sm:min-w-[80px] hover:scale-105 transition-transform duration-200">
                      <div className="text-lg sm:text-xl font-bold text-gray-700 dark:text-gray-300">
                        {user.liked_movies.length}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
                        <span>👍</span>
                        <span className="hidden sm:inline">curtidos</span>
                      </div>
                    </div>
                    <div className="glass rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-center min-w-[70px] sm:min-w-[80px] hover:scale-105 transition-transform duration-200">
                      <div className="text-lg sm:text-xl font-bold text-gray-700 dark:text-gray-300">
                        {user.disliked_movies.length}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
                        <span>👎</span>
                        <span className="hidden sm:inline">não curti</span>
                      </div>
                    </div>
                    <div className="glass rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-center min-w-[70px] sm:min-w-[80px] hover:scale-105 transition-transform duration-200">
                      <div className="text-lg sm:text-xl font-bold text-gray-700 dark:text-gray-300">
                        {stats.totalRatings}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
                        <span>⭐</span>
                        <span className="hidden sm:inline">avaliações</span>
                      </div>
                    </div>
                    {stats.avgRating > 0 && (
                      <div className="glass rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-center min-w-[70px] sm:min-w-[80px] hover:scale-105 transition-transform duration-200">
                        <div className="text-lg sm:text-xl font-bold text-gray-700 dark:text-gray-300">
                          {stats.avgRating.toFixed(1)}★
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="hidden sm:inline">média</span>
                        </div>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="glass rounded-xl px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/20 transition-colors"
                  >
                    Sair
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="glass rounded-xl px-4 py-2 text-sm font-medium bg-gradient-to-r from-gray-600 to-gray-800 text-white hover:from-gray-700 hover:to-gray-900 transition-all"
                >
                  Entrar / Registrar
                </button>
              )}
            </div>
          </div>
        </header>

        {error && (
          <div className="glass-strong rounded-xl p-4 border-l-4 border-red-500 bg-red-50/50 dark:bg-red-900/20 animate-slide-up">
            <p className="text-red-800 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Recomendações */}
        {user &&
          (user.liked_movies.length > 0 || user.disliked_movies.length > 0) && (
            <section className="glass-strong rounded-2xl p-4 sm:p-6 lg:p-8 shadow-xl animate-slide-up">
              <h2 className="text-2xl sm:text-3xl font-bold mb-4 sm:mb-6 flex items-center gap-3">
                <span>✨</span>
                <span className="bg-gradient-to-r from-gray-700 to-gray-900 dark:from-gray-300 dark:to-gray-100 bg-clip-text text-transparent">
                  Recomendações para Você
                </span>
              </h2>

              {recs.length === 0 ? (
                <div className="text-center py-12 sm:py-16 space-y-4">
                  <div className="text-6xl sm:text-7xl">👋</div>
                  <p className="text-base sm:text-lg text-gray-600 dark:text-gray-400">
                    Curta alguns filmes para começar a receber recomendações
                    personalizadas!
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
                  {recs.map((r) => (
                    <div key={r.movie.id} className="space-y-2">
                      <MovieCard
                        movie={r.movie}
                        userRating={user?.ratings[r.movie.id] || 0}
                        isLiked={
                          user?.liked_movies.includes(r.movie.id) || false
                        }
                        isDisliked={
                          user?.disliked_movies.includes(r.movie.id) || false
                        }
                        onRate={(stars) => handleRate(r.movie.id, stars)}
                        onVote={(action) => onVote(r.movie.id, action)}
                      />
                      <div className="glass rounded-lg p-3">
                        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                          <span className="font-semibold">💡 Por que?</span>{" "}
                          {r.reason}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

        {/* Catálogo */}
        <section className="glass-strong rounded-2xl p-4 sm:p-6 lg:p-8 shadow-xl space-y-4 sm:space-y-6 animate-slide-up">
          <div className="flex flex-col sm:flex-row gap-4 sm:items-center sm:justify-between">
            <h2 className="text-2xl sm:text-3xl font-bold flex items-center gap-3">
              <span>🎥</span>
              <span className="bg-gradient-to-r from-gray-700 to-gray-900 dark:from-gray-300 dark:to-gray-100 bg-clip-text text-transparent">
                Catálogo ({filtered.length} filmes)
              </span>
            </h2>

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por título, diretor, gênero..."
              className="w-full sm:w-80 px-4 py-3 rounded-xl glass focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>

          {/* Filtros */}
          <div className="glass-strong rounded-xl overflow-hidden border border-gray-200/50 dark:border-gray-700/50">
            {/* Header dos Filtros */}
            <div className="flex items-center justify-between p-4 sm:p-5 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-gray-50/50 to-slate-50/50 dark:from-gray-800/30 dark:to-slate-800/30">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🎯</span>
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200">
                  Filtros
                </h3>
                {(selectedGenres.size > 0 ||
                  yearRange[0] !== yearBounds.min ||
                  yearRange[1] !== yearBounds.max) && (
                  <span className="px-2.5 py-1 rounded-full bg-gray-600 dark:bg-gray-500 text-white text-xs font-semibold">
                    {selectedGenres.size +
                      (yearRange[0] !== yearBounds.min ||
                      yearRange[1] !== yearBounds.max
                        ? 1
                        : 0)}
                  </span>
                )}
              </div>
              {(selectedGenres.size > 0 ||
                yearRange[0] !== yearBounds.min ||
                yearRange[1] !== yearBounds.max) && (
                <button
                  onClick={() => {
                    setSelectedGenres(new Set());
                    setYearRange([yearBounds.min, yearBounds.max]);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-200/50 dark:hover:bg-gray-700/50 transition-all duration-200"
                >
                  Limpar filtros
                </button>
              )}
            </div>

            <div className="p-4 sm:p-5 space-y-6">
              {/* Gêneros */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">🎭</span>
                  <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Gêneros
                  </label>
                  {selectedGenres.size > 0 && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ({selectedGenres.size} selecionado
                      {selectedGenres.size > 1 ? "s" : ""})
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  {allGenres.map((genre) => (
                    <button
                      key={genre}
                      onClick={() => toggleGenre(genre)}
                      className={`group px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                        selectedGenres.has(genre)
                          ? "bg-gradient-to-r from-gray-600 to-gray-800 text-white shadow-md scale-105 ring-2 ring-gray-600/50"
                          : "glass hover:scale-105 hover:shadow-md text-gray-700 dark:text-gray-300"
                      }`}
                    >
                      <span className="flex items-center gap-1.5">
                        {selectedGenres.has(genre) && (
                          <span className="text-xs">✓</span>
                        )}
                        {genre}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Separador */}
              <div className="h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>

              {/* Ano e Ordenação */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Filtro de Ano */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">📅</span>
                    <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      Período
                    </label>
                  </div>
                  <div className="p-4 rounded-lg bg-gray-50/50 dark:bg-gray-800/30 space-y-4">
                    {/* Inputs manuais */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1.5">
                        <label className="text-xs text-gray-600 dark:text-gray-400 font-medium">
                          De
                        </label>
                        <input
                          type="number"
                          min={yearBounds.min}
                          max={yearBounds.max}
                          value={yearRange[0]}
                          onBlur={(e) => {
                            const val = Math.max(
                              yearBounds.min,
                              Math.min(+e.target.value, yearRange[1]),
                            );
                            setYearRange([val, yearRange[1]]);
                          }}
                          onChange={(e) => {
                            const val = +e.target.value;
                            if (!isNaN(val)) {
                              setYearRange([val, yearRange[1]]);
                            }
                          }}
                          className="w-full px-3 py-2 rounded-lg glass focus:ring-2 focus:ring-gray-600 dark:focus:ring-gray-400 focus:outline-none transition-all duration-200 text-gray-900 dark:text-white font-semibold text-center"
                        />
                      </div>
                      <div className="space-y-1.5">
                        <label className="text-xs text-gray-600 dark:text-gray-400 font-medium">
                          Até
                        </label>
                        <input
                          type="number"
                          min={yearBounds.min}
                          max={yearBounds.max}
                          value={yearRange[1]}
                          onBlur={(e) => {
                            const val = Math.min(
                              yearBounds.max,
                              Math.max(+e.target.value, yearRange[0]),
                            );
                            setYearRange([yearRange[0], val]);
                          }}
                          onChange={(e) => {
                            const val = +e.target.value;
                            if (!isNaN(val)) {
                              setYearRange([yearRange[0], val]);
                            }
                          }}
                          className="w-full px-3 py-2 rounded-lg glass focus:ring-2 focus:ring-gray-600 dark:focus:ring-gray-400 focus:outline-none transition-all duration-200 text-gray-900 dark:text-white font-semibold text-center"
                        />
                      </div>
                    </div>

                    {/* Range disponível */}
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 font-medium px-1">
                      <span>Disponível: {yearBounds.min}</span>
                      <span>{yearBounds.max}</span>
                    </div>
                  </div>
                </div>

                {/* Ordenação */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🔄</span>
                    <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      Ordenação
                    </label>
                  </div>
                  <div className="p-4 rounded-lg bg-gray-50/50 dark:bg-gray-800/30">
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as any)}
                      className="w-full px-4 py-3 rounded-lg glass focus:ring-2 focus:ring-gray-600 dark:focus:ring-gray-400 focus:outline-none transition-all duration-200 text-gray-900 dark:text-white cursor-pointer font-medium shadow-sm"
                    >
                      <option value="year">📆 Ano (mais recente)</option>
                      <option value="title">🔤 Título (A-Z)</option>
                      <option value="rating">⭐ Avaliação</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Paginação */}
          {pagination.totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 flex-wrap">
              <button
                onClick={pagination.prevPage}
                disabled={!pagination.hasPrev}
                className="px-4 py-2 rounded-lg glass hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-medium"
              >
                ← Anterior
              </button>

              <div className="flex gap-2">
                {Array.from(
                  { length: Math.min(5, pagination.totalPages) },
                  (_, i) => {
                    const pageNum = i + 1;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => pagination.goToPage(pageNum)}
                        className={`w-10 h-10 rounded-lg font-semibold transition-all ${
                          pagination.currentPage === pageNum
                            ? "bg-gradient-to-r from-gray-600 to-gray-800 text-white shadow-lg scale-110"
                            : "glass hover:scale-105"
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  },
                )}
              </div>

              <button
                onClick={pagination.nextPage}
                disabled={!pagination.hasNext}
                className="px-4 py-2 rounded-lg glass hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-medium"
              >
                Próximo →
              </button>

              <span className="text-sm text-gray-600 dark:text-gray-400 ml-4">
                Página {pagination.currentPage} de {pagination.totalPages} (
                {pagination.totalItems} filmes)
              </span>
            </div>
          )}

          {/* Grid de Filmes */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
            {pagination.items.map((m) => (
              <MovieCard
                key={m.id}
                movie={m}
                userRating={user?.ratings[m.id] || 0}
                isLiked={user?.liked_movies.includes(m.id) || false}
                isDisliked={user?.disliked_movies.includes(m.id) || false}
                onRate={(stars) => handleRate(m.id, stars)}
                onVote={(action) => onVote(m.id, action)}
              />
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="glass rounded-xl p-4 sm:p-6 text-center text-sm sm:text-base text-gray-600 dark:text-gray-400 animate-fade-in">
          <p className="flex items-center justify-center gap-2">
            <span>💡</span>
            <span>
              Dica: Curta 3-5 filmes e avalie para obter recomendações mais
              precisas!
            </span>
          </p>
        </footer>
      </div>
    </div>
  );
}
