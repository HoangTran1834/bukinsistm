import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";
import { type UserRole } from "../constants/roles";
import { authAPI, tokenUtils, userAPI } from "../services/api";

// Types
interface User {
  manguoidung: number;
  hoten: string;
  sodienthoai: string;
  email?: string;
  vaitro: UserRole;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (sodienthoai: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (userData: {
    hoten: string;
    sodienthoai: string;
    password: string;
    email?: string;
  }) => Promise<void>;
  error: string | null;
}

// Create the context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  logout: async () => {},
  signup: async () => {},
  error: null,
});

// Hook to use the auth context
export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

// Provider component
export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing token and load user data on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        if (tokenUtils.isAuthenticated()) {
          const response = await userAPI.getProfile();
          setUser(response.data);
        }
      } catch (err) {
        console.error("Failed to load user:", err);
        tokenUtils.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  // Login function
  const login = async (sodienthoai: string, password: string) => {
    setError(null);
    try {
      setIsLoading(true);
      const data = await authAPI.login({ sodienthoai, password });
      setUser(data.user);
      return data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setIsLoading(true);
      await authAPI.logout();
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setIsLoading(false);
    }
  };

  // Signup function
  const signup = async (userData: {
    hoten: string;
    sodienthoai: string;
    password: string;
    email?: string;
  }) => {
    setError(null);
    try {
      setIsLoading(true);
      await authAPI.signup(userData);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Registration failed. Please try again."
      );
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    signup,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
