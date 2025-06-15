import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { User, AuthTokens, LoginCredentials, SignupData, UserRole } from '@/types';
import { authAPI, userAPI } from '@/services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (userData: SignupData) => Promise<void>;
  logout: () => Promise<void>;
  isAdmin: boolean;
  isDriver: boolean;
  isStaff: boolean;
  isPassenger: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          const userData = await userAPI.getProfile();
          setUser(userData);
        } catch (error) {
          console.error('Failed to load user profile:', error);
          // Clear tokens if loading user fails
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      
      setIsLoading(false);
    };
    
    loadUser();
  }, []);
  
  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      const tokens = await authAPI.login(credentials);
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      const userData = await userAPI.getProfile();
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  const signup = async (userData: SignupData) => {
    setIsLoading(true);
    try {
      await authAPI.signup(userData);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  const logout = async () => {
    setIsLoading(true);
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authAPI.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local storage and state, even if API call fails
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsLoading(false);
    }
  };

  // Role-based helpers
  const isAdmin = user?.vaitro === UserRole.Admin;
  const isDriver = user?.vaitro === UserRole.Driver;
  const isStaff = user?.vaitro === UserRole.Staff;
  const isPassenger = user?.vaitro === UserRole.Passenger;
  
  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    isAdmin,
    isDriver,
    isStaff,
    isPassenger
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
        loading: false,
        error: null
      });
      
      navigate('/login');
    } catch (error) {
      // Even if logout fails on the server, clear client-side state
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null
      });
      
      navigate('/login');
    }
  };
  
  const updateProfile = async (data: Partial<User>) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));
      
      const updatedUser = await userAPI.updateProfile(data);
      
      setAuthState(prev => ({
        ...prev,
        user: updatedUser,
        loading: false
      }));
    } catch (error: any) {
      setAuthState(prev => ({ 
        ...prev, 
        loading: false,
        error: error.response?.data?.message || 'Failed to update profile.'
      }));
    }
  };
  
  const value = {
    ...authState,
    login,
    signup,
    logout,
    updateProfile
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
