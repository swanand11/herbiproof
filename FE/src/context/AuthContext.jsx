import {createContext,useState,useEffect} from "react";

import {api} from '../services/apis'

import { getToken, setToken, removeToken } from "../utils/TokenStorage";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);   // {id, username, role, kyc_status, token}
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (token) {
      api.get("/auth/me")
        .then(res => setUser({ ...res.data, token }))
        .catch(() => {
          removeToken();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // Login
  const login = async (username, password) => {
    const res = await api.post("/auth/login", { username, password });
    setToken(res.data.token);
    setUser(res.data.user);
    return res.data.user;
  };

  // Logout
  const logout = () => {
    removeToken();
    setUser(null);
  };

  const value = { user, login, logout, loading };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};