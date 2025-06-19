import React, { createContext, useState, useEffect, useContext } from "react";
import api, { UserResponse } from "@/api/backend";

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserResponse | null;
  login: (sodienthoai: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (
    fullName: string,
    phone: string,
    password: string,
    email?: string
  ) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Check if user is authenticated on component mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const userData = await api.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          console.error("Failed to authenticate with token:", error);
          // Clear invalid tokens
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (sodienthoai: string, password: string) => {
    try {
      const response = await api.login({ sodienthoai, password });
      localStorage.setItem("access_token", response.access);
      localStorage.setItem("refresh_token", response.refresh);

      // Fetch current user data
      const userData = await api.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        await api.logout(refreshToken);
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const register = async (
    hoten: string,
    sodienthoai: string,
    password: string,
    email?: string
  ) => {
    try {
      await api.signup({ hoten, sodienthoai, password, email });
      // Auto-login after registration
      await login(sodienthoai, password);
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    }
  };

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
    register,
  };

  if (loading) {
    // You can replace this with a proper loading component
    return <div>Loading...</div>;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
