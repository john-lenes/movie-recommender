import { useEffect, useMemo, useState } from 'react';
import type { Movie, User } from '../api';

interface UseMovieFiltersProps {
  movies: Movie[];
  user: User | null;
}

export function useMovieFilters({ movies, user }: UseMovieFiltersProps) {
  const [query, setQuery] = useState('');
  const [selectedGenres, setSelectedGenres] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'year' | 'title' | 'rating'>('year');
  const [yearRange, setYearRange] = useState<[number, number]>([1990, 2025]);

  const allGenres = useMemo(() => {
    const genres = new Set<string>();
    movies.forEach((m) => m.genres.forEach((g) => genres.add(g)));
    return Array.from(genres).sort();
  }, [movies]);

  const yearBounds = useMemo(() => {
    if (movies.length === 0) return { min: 1990, max: 2025 };
    const years = movies.map(m => m.year);
    return {
      min: Math.min(...years),
      max: Math.max(...years)
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
      const matchesQuery = !q || [m.title, m.director, m.genres.join(' '), String(m.year)].some((x) => 
        x.toLowerCase().includes(q)
      );
      const matchesGenres = selectedGenres.size === 0 || m.genres.some((g) => selectedGenres.has(g));
      const matchesYear = m.year >= yearRange[0] && m.year <= yearRange[1];
      return matchesQuery && matchesGenres && matchesYear;
    });

    // Ordenar
    if (sortBy === 'year') {
      result.sort((a, b) => b.year - a.year);
    } else if (sortBy === 'title') {
      result.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortBy === 'rating') {
      const userRatings = user?.ratings || {};
      result.sort((a, b) => (userRatings[b.id] || 0) - (userRatings[a.id] || 0));
    }

    return result;
  }, [movies, query, selectedGenres, yearRange, sortBy, user]);

  const toggleGenre = (genre: string) => {
    const next = new Set(selectedGenres);
    if (next.has(genre)) {
      next.delete(genre);
    } else {
      next.add(genre);
    }
    setSelectedGenres(next);
  };

  const clearFilters = () => {
    setSelectedGenres(new Set());
    setYearRange([yearBounds.min, yearBounds.max]);
    setQuery('');
  };

  return {
    query,
    setQuery,
    selectedGenres,
    toggleGenre,
    sortBy,
    setSortBy,
    yearRange,
    setYearRange,
    allGenres,
    yearBounds,
    filtered,
    clearFilters
  };
}
