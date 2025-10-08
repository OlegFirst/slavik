import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Keycloak from 'keycloak-js';
import { config } from '../config/environment';

interface KeycloakAuthContextType {
  keycloak: Keycloak | null;
  authenticated: boolean;
  loading: boolean;
  user: any;
  login: () => void;
  logout: () => void;
  hasRole: (role: string) => boolean;
  token: string | undefined;
}

const KeycloakAuthContext = createContext<KeycloakAuthContextType | undefined>(undefined);

// Check if Keycloak should be disabled
const DISABLE_KEYCLOAK = true; // TODO: Change to environment variable

export const KeycloakAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [keycloak, setKeycloak] = useState<Keycloak | null>(null);
  const [authenticated, setAuthenticated] = useState(DISABLE_KEYCLOAK ? true : false);
  const [loading, setLoading] = useState(!DISABLE_KEYCLOAK);
  const [user, setUser] = useState<any>(DISABLE_KEYCLOAK ? {
    username: 'admin',
    email: 'admin@bcm-platform.local',
    firstName: 'Admin',
    lastName: 'User'
  } : null);

  useEffect(() => {
    // Skip Keycloak initialization if disabled
    if (DISABLE_KEYCLOAK) {
      setLoading(false);
      return;
    }

    const initKeycloak = async () => {
      const kc = new Keycloak({
        url: config.keycloak.url,
        realm: config.keycloak.realm,
        clientId: config.keycloak.clientId
      });

      try {
        const authenticated = await kc.init({
          onLoad: 'check-sso',
          checkLoginIframe: false,
          pkceMethod: 'S256' // Security enhancement
        });

        setKeycloak(kc);
        setAuthenticated(authenticated);

        if (authenticated) {
          // Load user profile
          const profile = await kc.loadUserProfile();
          setUser(profile);

          // Setup token refresh
          setupTokenRefresh(kc);
        }
      } catch (error) {
        console.error('Keycloak initialization failed:', error);
        // Fallback to no auth when Keycloak fails
        setAuthenticated(true);
        setUser({
          username: 'fallback',
          email: 'fallback@bcm-platform.local'
        });
      } finally {
        setLoading(false);
      }
    };

    initKeycloak();
  }, []);

  const setupTokenRefresh = (kc: Keycloak) => {
    // Refresh token before expiration
    setInterval(() => {
      kc.updateToken(70).then((refreshed) => {
        if (refreshed) {
          console.debug('Token refreshed');
        }
      }).catch(() => {
        console.warn('Failed to refresh token');
        kc.login();
      });
    }, 60000); // Check every minute
  };

  const login = () => {
    if (DISABLE_KEYCLOAK) {
      console.log('Keycloak is disabled - auto-login as admin');
      setAuthenticated(true);
      return;
    }
    keycloak?.login({
      redirectUri: window.location.origin + '/admin'
    });
  };

  const logout = () => {
    if (DISABLE_KEYCLOAK) {
      console.log('Keycloak is disabled - logout simulation');
      setAuthenticated(false);
      return;
    }
    keycloak?.logout({
      redirectUri: window.location.origin
    });
  };

  const hasRole = (role: string): boolean => {
    if (DISABLE_KEYCLOAK) return true; // Grant all roles when disabled
    return keycloak?.hasRealmRole(role) ||
           keycloak?.hasResourceRole(role, config.keycloak.clientId) ||
           false;
  };

  const value: KeycloakAuthContextType = {
    keycloak,
    authenticated,
    loading,
    user,
    login,
    logout,
    hasRole,
    token: DISABLE_KEYCLOAK ? 'mock-token' : keycloak?.token
  };

  return (
    <KeycloakAuthContext.Provider value={value}>
      {children}
    </KeycloakAuthContext.Provider>
  );
};

export const useKeycloakAuth = () => {
  const context = useContext(KeycloakAuthContext);
  if (!context) {
    throw new Error('useKeycloakAuth must be used within KeycloakAuthProvider');
  }
  return context;
};

// HOC for protected routes
export const withKeycloakAuth = <P extends object>(
  Component: React.ComponentType<P>,
  requiredRoles: string[] = []
) => {
  return (props: P) => {
    const { authenticated, loading, hasRole } = useKeycloakAuth();

    if (loading) {
      return <div>Loading authentication...</div>;
    }

    if (!authenticated) {
      return <div>Please log in to access this page.</div>;
    }

    if (requiredRoles.length > 0 && !requiredRoles.some(role => hasRole(role))) {
      return <div>Access denied. Insufficient permissions.</div>;
    }

    return <Component {...props} />;
  };
};