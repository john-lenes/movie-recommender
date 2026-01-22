export type CollectionInfo = {
  id: number;
  name: string;
  poster_path?: string | null;
  backdrop_path?: string | null;
};

export type SpokenLanguage = {
  iso_639_1: string;
  name: string;
  english_name?: string;
};

export type RatingStats = {
  average?: number;
  count?: number;
  min?: number;
  max?: number;
};

export type Movie = {
  id: number;
  title: string;
  year: number;
  genres: string[];
  director: string;
  description: string;

  // IDs externos
  tmdb_id?: number | null;
  imdb_id?: string | null;

  // Informações básicas TMDB
  original_title?: string | null;
  original_language?: string | null;
  overview?: string | null;
  tagline?: string | null;
  runtime?: number | null;
  release_date?: string | null;

  // Avaliações e popularidade
  vote_average?: number | null;
  vote_count?: number | null;
  popularity?: number | null;
  rating_stats?: RatingStats | null;

  // Conteúdo rico
  keywords?: string[];
  cast?: string[];
  production_companies?: string[];
  production_countries?: string[];

  // Imagens
  poster_path?: string | null;
  backdrop_path?: string | null;

  // Flags
  adult?: boolean | null;
  video?: boolean | null;

  // Dados financeiros
  budget?: number | null;
  revenue?: number | null;

  // Coleção/Franquia
  belongs_to_collection?: CollectionInfo | null;

  // Idiomas e certificação
  spoken_languages?: SpokenLanguage[];
  original_language_name?: string | null;
  certification?: string | null;

  // Status
  status?: string | null;

  // Métricas derivadas (calculadas)
  roi?: number | null;
  popularity_tier?: string | null;
  decade?: string | null;
  score_composite?: number | null;
  trending_score?: number | null;
};

export type Recommendation = {
  movie: Movie;
  score: number;
  reason: string;
};

export type RecommendationResponse = {
  liked_ids: number[];
  recommendations: Recommendation[];
};

export type User = {
  id: number;
  username: string;
  email: string;
  created_at: string;
  liked_movies: number[];
  disliked_movies: number[];
  ratings: Record<number, number>;
};

export type AuthResponse = {
  user: User;
  token: string;
};

const BASE = "/api";
let authToken: string | null = localStorage.getItem("authToken");

// Retry com exponential backoff
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 3,
): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000); // 10s timeout

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeout);
      return response;
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise((resolve) =>
        setTimeout(resolve, Math.pow(2, i) * 1000),
      );
    }
  }
  throw new Error("Max retries reached");
}

function getHeaders() {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
}

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem("authToken", token);
  } else {
    localStorage.removeItem("authToken");
  }
}

export function getAuthToken() {
  return authToken;
}

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  const r = await fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  if (!r.ok) {
    const error = await r
      .json()
      .catch(() => ({ detail: "Registration failed" }));
    throw new Error(error.detail || "Registration failed");
  }
  const data = await r.json();
  setAuthToken(data.token);
  return data;
}

export async function login(
  username: string,
  password: string,
): Promise<AuthResponse> {
  const r = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!r.ok) {
    const error = await r.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(error.detail || "Login failed");
  }
  const data = await r.json();
  setAuthToken(data.token);
  return data;
}

export async function logout() {
  try {
    await fetch(`${BASE}/auth/logout`, {
      method: "POST",
      headers: getHeaders(),
    });
  } finally {
    setAuthToken(null);
  }
}

export async function getMe(): Promise<User> {
  const r = await fetchWithRetry(`${BASE}/auth/me`, { headers: getHeaders() });
  if (!r.ok) throw new Error("Não autenticado");
  return r.json();
}

export async function getMovies(): Promise<Movie[]> {
  try {
    const r = await fetchWithRetry(`${BASE}/movies`);
    if (!r.ok) {
      throw new Error(`Erro ao carregar filmes: ${r.status} ${r.statusText}`);
    }
    const data = await r.json();
    if (!Array.isArray(data)) {
      throw new Error("Formato de dados inválido");
    }
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("Timeout: Servidor demorou muito para responder");
    }
    throw error;
  }
}

export async function sendFeedback(
  movieId: number,
  action: "like" | "dislike",
) {
  const r = await fetch(`${BASE}/feedback`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ movie_id: movieId, action }),
  });
  if (!r.ok) throw new Error("Failed to send feedback");
  return r.json();
}

export async function rateMovie(movieId: number, rating: number) {
  const r = await fetch(`${BASE}/rating`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ movie_id: movieId, rating }),
  });
  if (!r.ok) throw new Error("Failed to rate movie");
  return r.json();
}

export async function getRecommendations(
  k = 10,
): Promise<RecommendationResponse> {
  const r = await fetch(`${BASE}/recommendations?k=${k}`, {
    headers: getHeaders(),
  });
  if (!r.ok) throw new Error("Failed to fetch recommendations");
  return r.json();
}
