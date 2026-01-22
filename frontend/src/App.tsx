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

// Mapeamento de ícones e cores para gêneros
const GENRE_CONFIG: Record<
  string,
  { icon: string; color: string; darkColor: string }
> = {
  Action: {
    icon: "💥",
    color: "bg-red-100 text-red-700 border-red-200",
    darkColor: "dark:bg-red-900/30 dark:text-red-300 dark:border-red-800",
  },
  Adventure: {
    icon: "🗺️",
    color: "bg-amber-100 text-amber-700 border-amber-200",
    darkColor: "dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800",
  },
  Animation: {
    icon: "🎨",
    color: "bg-purple-100 text-purple-700 border-purple-200",
    darkColor:
      "dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-800",
  },
  Comedy: {
    icon: "😄",
    color: "bg-yellow-100 text-yellow-700 border-yellow-200",
    darkColor:
      "dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800",
  },
  Crime: {
    icon: "🔫",
    color: "bg-slate-100 text-slate-700 border-slate-200",
    darkColor: "dark:bg-slate-900/30 dark:text-slate-300 dark:border-slate-800",
  },
  Documentary: {
    icon: "🎥",
    color: "bg-teal-100 text-teal-700 border-teal-200",
    darkColor: "dark:bg-teal-900/30 dark:text-teal-300 dark:border-teal-800",
  },
  Drama: {
    icon: "🎭",
    color: "bg-indigo-100 text-indigo-700 border-indigo-200",
    darkColor:
      "dark:bg-indigo-900/30 dark:text-indigo-300 dark:border-indigo-800",
  },
  Fantasy: {
    icon: "🧙",
    color: "bg-violet-100 text-violet-700 border-violet-200",
    darkColor:
      "dark:bg-violet-900/30 dark:text-violet-300 dark:border-violet-800",
  },
  Horror: {
    icon: "👻",
    color: "bg-red-100 text-red-800 border-red-300",
    darkColor: "dark:bg-red-950/50 dark:text-red-400 dark:border-red-900",
  },
  Mystery: {
    icon: "🔍",
    color: "bg-slate-100 text-slate-800 border-slate-200",
    darkColor: "dark:bg-slate-900/40 dark:text-slate-300 dark:border-slate-800",
  },
  Romance: {
    icon: "💕",
    color: "bg-pink-100 text-pink-700 border-pink-200",
    darkColor: "dark:bg-pink-900/30 dark:text-pink-300 dark:border-pink-800",
  },
  "Science Fiction": {
    icon: "🚀",
    color: "bg-blue-100 text-blue-700 border-blue-200",
    darkColor: "dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800",
  },
  "Sci-Fi": {
    icon: "🚀",
    color: "bg-blue-100 text-blue-700 border-blue-200",
    darkColor: "dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800",
  },
  Thriller: {
    icon: "⚡",
    color: "bg-orange-100 text-orange-700 border-orange-200",
    darkColor:
      "dark:bg-orange-900/30 dark:text-orange-300 dark:border-orange-800",
  },
  War: {
    icon: "⚔️",
    color: "bg-red-100 text-red-800 border-red-200",
    darkColor: "dark:bg-red-900/40 dark:text-red-300 dark:border-red-800",
  },
  Western: {
    icon: "🤠",
    color: "bg-amber-100 text-amber-800 border-amber-200",
    darkColor: "dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800",
  },
  Music: {
    icon: "🎵",
    color: "bg-fuchsia-100 text-fuchsia-700 border-fuchsia-200",
    darkColor:
      "dark:bg-fuchsia-900/30 dark:text-fuchsia-300 dark:border-fuchsia-800",
  },
  History: {
    icon: "📜",
    color: "bg-stone-100 text-stone-700 border-stone-200",
    darkColor: "dark:bg-stone-900/30 dark:text-stone-300 dark:border-stone-800",
  },
  Family: {
    icon: "👨‍👩‍👧‍👦",
    color: "bg-emerald-100 text-emerald-700 border-emerald-200",
    darkColor:
      "dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-800",
  },
};

const Badge = memo(function Badge({
  children,
  variant = "default",
}: {
  children: string;
  variant?: "default" | "neutral";
}) {
  const baseClasses =
    "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border transition-all duration-200 hover:scale-105";

  const config = GENRE_CONFIG[children];
  const variantClasses = config
    ? `${config.color} ${config.darkColor}`
    : variant === "neutral"
      ? "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700"
      : "bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300 border-primary-200 dark:border-primary-800";

  return (
    <span className={`${baseClasses} ${variantClasses}`}>
      {config && <span>{config.icon}</span>}
      {children}
    </span>
  );
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
  const posterUrl = m.poster_path
    ? `https://image.tmdb.org/t/p/w500${m.poster_path}`
    : null;

  return (
    <div className="group glass rounded-xl p-5 space-y-4 transition-all duration-300 shadow-lg hover:shadow-2xl hover:scale-[1.02] flex flex-col">
      <div className="flex items-start gap-4">
        {posterUrl ? (
          <div className="relative flex-shrink-0">
            <img
              src={posterUrl}
              alt={m.title}
              loading="lazy"
              className="object-cover rounded-lg shadow-lg w-28 h-40 transition-transform duration-300 group-hover:scale-105"
            />
            {m.vote_average && m.vote_average >= 8 && (
              <div className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 rounded-full w-10 h-10 flex items-center justify-center shadow-lg font-bold text-sm border-2 border-white dark:border-gray-800">
                ⭐
              </div>
            )}
          </div>
        ) : (
          <div className="w-28 h-40 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 rounded-lg flex items-center justify-center shadow-inner flex-shrink-0">
            <span className="text-5xl opacity-50">🎬</span>
          </div>
        )}
        <div className="flex-1 min-w-0 space-y-2">
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white leading-tight mb-1 line-clamp-2 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-colors">
              {m.title}
            </h3>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-semibold">
                📅 {m.year}
              </span>
              {m.vote_average && (
                <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 text-xs font-semibold">
                  <span>⭐</span>
                  <span>{m.vote_average.toFixed(1)}</span>
                  {m.vote_count && (
                    <span className="text-[10px] opacity-75">
                      (
                      {m.vote_count > 1000
                        ? `${(m.vote_count / 1000).toFixed(1)}k`
                        : m.vote_count}
                      )
                    </span>
                  )}
                </div>
              )}
              {m.director && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-semibold truncate max-w-[150px]">
                  🎬 {m.director}
                </span>
              )}
            </div>
          </div>
          {m.certification && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 border border-red-200 dark:border-red-800">
              {m.certification}
            </span>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {m.genres.slice(0, 4).map((g) => (
          <Badge key={g}>{g}</Badge>
        ))}
        {m.genres.length > 4 && (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
            +{m.genres.length - 4}
          </span>
        )}
      </div>

      <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-3">
          {m.description || m.overview || "Sem sinopse disponível"}
        </p>
        {(m.runtime || m.budget || m.revenue) && (
          <div className="flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400">
            {m.runtime && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
                ⏱️ {m.runtime} min
              </span>
            )}
            {m.budget && m.budget > 0 && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
                💰 ${(m.budget / 1000000).toFixed(0)}M
              </span>
            )}
            {m.revenue && m.revenue > 0 && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                📈 ${(m.revenue / 1000000).toFixed(0)}M
              </span>
            )}
          </div>
        )}
      </div>

      {/* Keywords/Tags */}
      {m.keywords && m.keywords.length > 0 && (
        <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm">🏷️</span>
            <p className="text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
              Temas
            </p>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {m.keywords.slice(0, 6).map((kw, idx) => (
              <span
                key={idx}
                className="text-[11px] px-2.5 py-1 bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-700 dark:text-gray-300 rounded-full font-medium hover:scale-105 transition-transform cursor-default border border-gray-200 dark:border-gray-600"
              >
                {kw}
              </span>
            ))}
            {m.keywords.length > 6 && (
              <span className="text-[11px] px-2.5 py-1 text-gray-500 dark:text-gray-500 font-medium">
                +{m.keywords.length - 6}
              </span>
            )}
          </div>
        </div>
      )}

      <div className="space-y-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
              Sua Avaliação
            </span>
            {userRating > 0 && (
              <span className="text-xs text-gray-500 dark:text-gray-500 font-medium">
                {userRating} estrela{userRating > 1 ? "s" : ""}
              </span>
            )}
          </div>
          <StarRating rating={userRating} onRate={onRate} />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => onVote("like")}
            className={`group py-2.5 rounded-lg text-center transition-all duration-200 font-semibold text-sm flex items-center justify-center gap-2 ${
              isLiked
                ? "bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg ring-2 ring-green-500/50"
                : "glass hover:scale-[1.02] hover:shadow-md text-gray-700 dark:text-gray-300"
            }`}
          >
            <span className="text-lg">{isLiked ? "✓" : "👍"}</span>
            <span>{isLiked ? "Curtido" : "Curtir"}</span>
          </button>
          <button
            onClick={() => onVote("dislike")}
            className={`group py-2.5 rounded-lg text-center transition-all duration-200 font-semibold text-sm flex items-center justify-center gap-2 ${
              isDisliked
                ? "bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-lg ring-2 ring-red-500/50"
                : "glass hover:scale-[1.02] hover:shadow-md text-gray-700 dark:text-gray-300"
            }`}
          >
            <span className="text-lg">{isDisliked ? "✗" : "👎"}</span>
            <span>{isDisliked ? "Não curti" : "Não curtir"}</span>
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
  const [showFilters, setShowFilters] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    "checking" | "connected" | "error"
  >("checking");

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
        setConnectionStatus("checking");

        const data = await getMovies();
        setMovies(data);
        setConnectionStatus("connected");

        if (data.length === 0) {
          setError("Nenhum filme disponível no momento");
        }

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
            setAuthToken(null);
          }
        }
      } catch (e: any) {
        setConnectionStatus("error");
        const errorMsg = e?.message ?? "Erro ao conectar com o servidor";
        setError(errorMsg);
        toast.error(errorMsg);
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
      toast.error("Faça login para curtir filmes");
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

      const movie = movies.find((m) => m.id === movieId);
      const movieTitle = movie ? ` "${movie.title}"` : "";
      toast.success(
        action === "like"
          ? `✓ Filme${movieTitle} curtido!`
          : `✓ Feedback registrado para${movieTitle}!`,
      );
    } catch (e: any) {
      const errorMsg = e?.message ?? "Erro ao registrar feedback";
      setError(errorMsg);
      toast.error(errorMsg);
    }
  }

  async function handleRate(movieId: number, stars: number) {
    if (!user) {
      toast.error("Faça login para avaliar filmes");
      setShowAuthModal(true);
      return;
    }

    if (stars < 1 || stars > 5) {
      toast.error("Avaliação deve ser entre 1 e 5 estrelas");
      return;
    }

    try {
      const movie = movies.find((m) => m.id === movieId);
      const response = await rateMovie(movieId, stars);
      setUser(response.user);
      const movieTitle = movie ? ` "${movie.title}"` : "";
      toast.success(
        `✓ ${movieTitle} avaliado com ${stars} estrela${stars > 1 ? "s" : ""}!`,
      );
    } catch (e: any) {
      const errorMsg = e?.message ?? "Erro ao registrar avaliação";
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
            {connectionStatus === "checking" && "Conectando ao servidor..."}
            {connectionStatus === "connected" && "Carregando filmes do TMDB..."}
            {connectionStatus === "error" && "Erro ao conectar com o servidor"}
          </p>
          {connectionStatus === "connected" && (
            <div className="flex items-center justify-center gap-2 text-sm text-green-600 dark:text-green-400">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span>Conectado</span>
            </div>
          )}
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
              <div className="flex items-center gap-3">
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                  {user
                    ? `Olá, ${user.username}! Sistema inteligente com dados do TMDB`
                    : "Sistema inteligente com dados do TMDB"}
                </p>
                {connectionStatus === "connected" && (
                  <span className="flex items-center gap-1.5 text-xs text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-full">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                    Online
                  </span>
                )}
              </div>
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

        {/* Catálogo com Sidebar */}
        <section className="relative">
          {/* Mobile Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="lg:hidden fixed bottom-6 right-6 z-40 p-4 rounded-full bg-gradient-to-r from-gray-600 to-gray-800 text-white shadow-2xl hover:scale-110 transition-all duration-200 flex items-center gap-2"
          >
            <span className="text-xl">🎯</span>
            {(selectedGenres.size > 0 ||
              yearRange[0] !== yearBounds.min ||
              yearRange[1] !== yearBounds.max) && (
              <span className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold">
                {selectedGenres.size +
                  (yearRange[0] !== yearBounds.min ||
                  yearRange[1] !== yearBounds.max
                    ? 1
                    : 0)}
              </span>
            )}
          </button>

          {/* Overlay para mobile */}
          {showFilters && (
            <div
              className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-30"
              onClick={() => setShowFilters(false)}
            />
          )}

          <div className="flex gap-6">
            {/* Sidebar de Filtros */}
            <aside
              className={`
                fixed lg:sticky top-0 left-0 lg:left-auto
                h-screen lg:h-auto lg:top-6
                w-80 lg:w-72 xl:w-80
                bg-white dark:bg-gray-900 lg:glass-strong
                rounded-none lg:rounded-2xl
                shadow-2xl lg:shadow-xl
                z-40 lg:z-auto
                transition-transform duration-300
                overflow-y-auto
                ${showFilters ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
              `}
            >
              {/* Header da Sidebar */}
              <div className="sticky top-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm p-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎯</span>
                  <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                    Filtros
                  </h3>
                  {(selectedGenres.size > 0 ||
                    yearRange[0] !== yearBounds.min ||
                    yearRange[1] !== yearBounds.max) && (
                    <span className="px-2.5 py-1 rounded-full bg-gray-600 text-white text-xs font-semibold">
                      {selectedGenres.size +
                        (yearRange[0] !== yearBounds.min ||
                        yearRange[1] !== yearBounds.max
                          ? 1
                          : 0)}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setShowFilters(false)}
                  className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <span className="text-2xl">✕</span>
                </button>
              </div>

              <div className="p-5 space-y-6">
                {/* Limpar Filtros */}
                {(selectedGenres.size > 0 ||
                  yearRange[0] !== yearBounds.min ||
                  yearRange[1] !== yearBounds.max) && (
                  <button
                    onClick={() => {
                      setSelectedGenres(new Set());
                      setYearRange([yearBounds.min, yearBounds.max]);
                    }}
                    className="w-full py-2.5 px-4 rounded-lg text-sm font-semibold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                  >
                    🗑️ Limpar todos os filtros
                  </button>
                )}

                {/* Gêneros */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🎭</span>
                    <label className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                      Gêneros
                    </label>
                    {selectedGenres.size > 0 && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        ({selectedGenres.size})
                      </span>
                    )}
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                    {allGenres.map((genre) => {
                      const config = GENRE_CONFIG[genre];
                      const isSelected = selectedGenres.has(genre);
                      return (
                        <button
                          key={genre}
                          onClick={() => toggleGenre(genre)}
                          className={`w-full px-3 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center gap-2.5 ${
                            isSelected
                              ? "bg-gradient-to-r from-gray-600 to-gray-800 text-white shadow-md"
                              : "glass hover:shadow-md text-gray-700 dark:text-gray-300"
                          }`}
                        >
                          {config && (
                            <span className="text-base">{config.icon}</span>
                          )}
                          <span className="flex-1 text-left">{genre}</span>
                          {isSelected && <span className="text-xs">✓</span>}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Separador */}
                <div className="h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>

                {/* Período */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">📅</span>
                    <label className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                      Período
                    </label>
                  </div>
                  <div className="space-y-4">
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
                    <div className="px-2">
                      <input
                        type="range"
                        min={yearBounds.min}
                        max={yearBounds.max}
                        value={yearRange[0]}
                        onChange={(e) =>
                          setYearRange([+e.target.value, yearRange[1]])
                        }
                        className="w-full"
                      />
                      <input
                        type="range"
                        min={yearBounds.min}
                        max={yearBounds.max}
                        value={yearRange[1]}
                        onChange={(e) =>
                          setYearRange([yearRange[0], +e.target.value])
                        }
                        className="w-full mt-2"
                      />
                    </div>
                  </div>
                </div>

                {/* Separador */}
                <div className="h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>

                {/* Ordenação */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🔄</span>
                    <label className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                      Ordenar por
                    </label>
                  </div>
                  <div className="space-y-2">
                    {(
                      [
                        { value: "year", label: "Ano", icon: "📅" },
                        { value: "title", label: "Título", icon: "🔤" },
                        { value: "rating", label: "Avaliação", icon: "⭐" },
                      ] as const
                    ).map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setSortBy(option.value)}
                        className={`w-full px-3 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center gap-2.5 ${
                          sortBy === option.value
                            ? "bg-gradient-to-r from-gray-600 to-gray-800 text-white shadow-md"
                            : "glass hover:shadow-md text-gray-700 dark:text-gray-300"
                        }`}
                      >
                        <span className="text-base">{option.icon}</span>
                        <span className="flex-1 text-left">{option.label}</span>
                        {sortBy === option.value && (
                          <span className="text-xs">✓</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </aside>

            {/* Área Principal do Catálogo */}
            <div className="flex-1 space-y-6">
              <div className="glass-strong rounded-2xl p-4 sm:p-6 lg:p-8 shadow-xl space-y-4 sm:space-y-6">
                <div className="flex flex-col sm:flex-row gap-4 sm:items-center sm:justify-between">
                  <h2 className="text-2xl sm:text-3xl font-bold flex items-center gap-3">
                    <span>🎥</span>
                    <span className="bg-gradient-to-r from-gray-700 to-gray-900 dark:from-gray-300 dark:to-gray-100 bg-clip-text text-transparent">
                      Catálogo
                    </span>
                    <span className="text-lg text-gray-500 dark:text-gray-400 font-normal">
                      ({filtered.length} filmes)
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
                      Página {pagination.currentPage} de {pagination.totalPages}{" "}
                      ({pagination.totalItems} filmes)
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
              </div>
            </div>
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
