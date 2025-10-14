import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { secureApiClient } from '../api/SecureApiClient';

interface SecureAuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkPermission: (permission: string) => boolean;
}

const SecureAuthContext = createContext<SecureAuthContextType | undefined>(undefined);

export const SecureAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  // Убираем localStorage - используем httpOnly cookies
  const checkAuth = async () => {
    try {
      // Валидация через server-side session
      const response = await secureApiClient.get('/auth/validate', {
        withCredentials: true // httpOnly cookies
      });
      setUser(response.data.user);
    } catch (error) {
      setUser(null);
    }
  };

  const login = async (email: string, password: string) => {
    // CSRF token включен автоматически
    const response = await secureApiClient.post('/auth/login', {
      email,
      password
    }, {
      withCredentials: true
    });

    setUser(response.data.user);
    // Токен сохраняется в httpOnly cookie на сервере
  };

  const logout = async () => {
    await secureApiClient.post('/auth/logout', {}, {
      withCredentials: true
    });
    setUser(null);
  };

  const checkPermission = (permission: string): boolean => {
    return user?.permissions?.includes(permission) || false;
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <SecureAuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      login,
      logout,
      checkPermission
    }}>
      {children}
    </SecureAuthContext.Provider>
  );
};

export const useSecureAuth = () => {
  const context = useContext(SecureAuthContext);
  if (!context) {
    throw new Error('useSecureAuth must be used within SecureAuthProvider');
  }
  return context;
};