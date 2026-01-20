import { useEffect, useState } from 'react';
import { logout as apiLogout, getAuthToken, getMe, type User } from '../api';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => {
          // Token inválido
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const logout = async () => {
    await apiLogout();
    setUser(null);
  };

  return {
    user,
    setUser,
    logout,
    isAuthenticated: !!user,
    loading
  };
}
