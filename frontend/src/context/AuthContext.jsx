import { createContext, useContext, useEffect, useState } from "react";
import * as authApi from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("tc_access");
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .fetchMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("tc_access");
        localStorage.removeItem("tc_refresh");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const handleExpiredSession = () => setUser(null);
    window.addEventListener("tc:logout", handleExpiredSession);
    return () => window.removeEventListener("tc:logout", handleExpiredSession);
  }, []);

  const persistTokens = (data) => {
    localStorage.setItem("tc_access", data.access);
    localStorage.setItem("tc_refresh", data.refresh);
  };

  const login = async (email, password) => {
    const data = await authApi.login({ email, password });
    persistTokens(data);
    const me = await authApi.fetchMe();
    setUser(me);
    return me;
  };

  const register = async (payload) => {
    const data = await authApi.register(payload);
    persistTokens(data);
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    const refresh = localStorage.getItem("tc_refresh");
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // Local sign-out still succeeds if the server cannot blacklist the token.
    } finally {
      localStorage.removeItem("tc_access");
      localStorage.removeItem("tc_refresh");
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
