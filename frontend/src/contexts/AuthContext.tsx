import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "../lib/api";
import type { User } from "../types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("cognify_token");
    const storedUser = localStorage.getItem("cognify_user");
    if (storedToken && storedUser) {
      setToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("cognify_user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post("/auth/login", { email, password });
    const { user: u, access_token } = data;
    localStorage.setItem("cognify_token", access_token);
    localStorage.setItem("cognify_user", JSON.stringify(u));
    setToken(access_token);
    setUser(u);
  }, []);

  const register = useCallback(async (email: string, username: string, password: string, full_name: string) => {
    const { data } = await api.post("/auth/register", { email, username, password, full_name });
    const { user: u, access_token } = data;
    localStorage.setItem("cognify_token", access_token);
    localStorage.setItem("cognify_user", JSON.stringify(u));
    setToken(access_token);
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("cognify_token");
    localStorage.removeItem("cognify_user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used within AuthProvider");
  return ctx;
}

export default AuthContext;
