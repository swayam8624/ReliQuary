// Multi-Tenant Authentication Service
// Integrates with backend multi-tenancy system for SaaS platform

import { useState, useEffect, useContext, createContext } from 'react';

// Types
interface Tenant {
  id: string;
  name: string;
  tier: 'free' | 'starter' | 'professional' | 'enterprise';
  createdAt: string;
  isActive: boolean;
  customDomains: string[];
  features: {
    customDomains: boolean;
    ssoIntegration: boolean;
    advancedAnalytics: boolean;
    prioritySupport: boolean;
    complianceReports: boolean;
    auditLogs: boolean;
    apiAccess: boolean;
    webhookNotifications: boolean;
    customIntegrations: boolean;
    dedicatedSupport: boolean;
    slaGuarantee: boolean;
    onPremiseDeployment: boolean;
    customSecurityPolicies: boolean;
    whiteLabelBranding: boolean;
  };
}

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'developer' | 'viewer' | 'billing';
  tenantId: string;
  createdAt: string;
  lastLogin: string;
}

interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface LoginCredentials {
  email: string;
  password: string;
  tenantDomain?: string;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  organization: string;
  tenantDomain?: string;
}

// Create context
const AuthContext = createContext<{
  authState: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  switchTenant: (tenantId: string) => Promise<void>;
  refreshAuth: () => Promise<void>;
}>({
  authState: {
    user: null,
    tenant: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  },
  login: async () => {},
  register: async () => {},
  logout: () => {},
  switchTenant: async () => {},
  refreshAuth: async () => {}
});

// Auth provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    tenant: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  // Initialize auth state from localStorage/sessionStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          await refreshAuth();
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setAuthState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginCredentials) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // In a real implementation, this would call your backend API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }

      const data = await response.json();
      
      // Store token
      localStorage.setItem('authToken', data.token);
      
      // Update state
      setAuthState({
        user: data.user,
        tenant: data.tenant,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
      
      // Store in sessionStorage for persistence
      sessionStorage.setItem('currentUser', JSON.stringify(data.user));
      sessionStorage.setItem('currentTenant', JSON.stringify(data.tenant));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }));
      throw error;
    }
  };

  // Register function
  const register = async (data: RegisterData) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // In a real implementation, this would call your backend API
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Registration failed');
      }

      const result = await response.json();
      
      // For registration, we might not immediately log in
      // but show a success message and redirect to login
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: null
      }));
      
      return result;
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed'
      }));
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('currentUser');
    sessionStorage.removeItem('currentTenant');
    
    setAuthState({
      user: null,
      tenant: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
    
    // Redirect to login page
    window.location.href = '/login';
  };

  // Switch tenant function
  const switchTenant = async (tenantId: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(`/api/auth/switch-tenant/${tenantId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to switch tenant');
      }

      const data = await response.json();
      
      // Update state with new tenant
      setAuthState(prev => ({
        ...prev,
        tenant: data.tenant,
        isLoading: false,
        error: null
      }));
      
      // Update sessionStorage
      sessionStorage.setItem('currentTenant', JSON.stringify(data.tenant));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to switch tenant'
      }));
      throw error;
    }
  };

  // Refresh auth function
  const refreshAuth = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No auth token found');
      }

      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Invalid token');
      }

      const data = await response.json();
      
      setAuthState({
        user: data.user,
        tenant: data.tenant,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
      
      // Update sessionStorage
      sessionStorage.setItem('currentUser', JSON.stringify(data.user));
      sessionStorage.setItem('currentTenant', JSON.stringify(data.tenant));
    } catch (error) {
      logout(); // Clear invalid auth state
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        authState,
        login,
        register,
        logout,
        switchTenant,
        refreshAuth
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Helper function to get tenant features
export function useTenantFeatures() {
  const { authState } = useAuth();
  
  return {
    hasFeature: (feature: keyof Tenant['features']) => {
      return authState.tenant?.features[feature] ?? false;
    },
    getQuota: (resource: string) => {
      // This would integrate with backend quota system
      return 0;
    },
    getUsage: (resource: string) => {
      // This would integrate with backend usage tracking
      return 0;
    }
  };
}

// Helper function to check user permissions
export function useUserPermissions() {
  const { authState } = useAuth();
  
  return {
    isAdmin: authState.user?.role === 'admin',
    isDeveloper: authState.user?.role === 'developer',
    isViewer: authState.user?.role === 'viewer',
    isBilling: authState.user?.role === 'billing',
    hasPermission: (permission: string) => {
      // This would integrate with backend RBAC system
      return true;
    }
  };
}