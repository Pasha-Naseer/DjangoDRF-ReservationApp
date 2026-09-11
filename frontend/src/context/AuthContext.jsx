import { createContext, useContext, useState } from "react";
import { apiFetch, setTokens, clearTokens, getTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  async function login(username, password) {
    const data = await apiFetch("/auth/login/", { method: "POST", body: { username, password } });
    setTokens(data);
    setUser(data.user);
    return data.user;
  }

  async function logout() {
    const { refresh } = getTokens();
    try {
      await apiFetch("/auth/logout/", { method: "POST", body: { refresh } });
    } catch {
      // token already invalid/expire; we're clearing it locally anyway
    }
    clearTokens();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
