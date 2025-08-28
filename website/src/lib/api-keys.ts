// API Key Management Service
// Comprehensive system for API key creation, management, rate limiting, and quota enforcement

import { useState, useEffect, useRef } from 'react';

// Types
interface ApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: string;
  lastUsed: string;
  expiresAt?: string;
  status: 'active' | 'inactive' | 'expired';
  permissions: string[];
  rateLimit: number; // requests per hour
  environment: 'development' | 'staging' | 'production';
  allowedIps?: string[];
  tenantId: string;
}

interface RateLimitInfo {
  keyId: string;
  requestsThisHour: number;
  resetTime: string;
  quotaUsed: number;
  quotaLimit: number;
}

interface QuotaConfig {
  [key: string]: {
    limit: number;
    period: 'hour' | 'day' | 'month';
  };
}

// Mock data for demonstration
const MOCK_API_KEYS: ApiKey[] = [
  {
    id: 'ak_abc123',
    name: 'Production API Key',
    key: 'rq_live_1234567890abcdef1234567890abcdef',
    createdAt: '2024-01-15T10:30:00Z',
    lastUsed: '2024-01-20T14:22:00Z',
    status: 'active',
    permissions: ['vault:read', 'vault:write', 'analytics:read'],
    rateLimit: 10000,
    environment: 'production',
    tenantId: 'tenant-1'
  },
  {
    id: 'ak_def456',
    name: 'Development Testing',
    key: 'rq_test_abcdef1234567890abcdef1234567890',
    createdAt: '2024-01-10T09:15:00Z',
    lastUsed: '2024-01-19T11:45:00Z',
    status: 'active',
    permissions: ['vault:read', 'vault:write'],
    rateLimit: 1000,
    environment: 'development',
    tenantId: 'tenant-1'
  }
];

const QUOTA_CONFIG: QuotaConfig = {
  'free': {
    limit: 1000,
    period: 'month'
  },
  'starter': {
    limit: 10000,
    period: 'month'
  },
  'professional': {
    limit: 100000,
    period: 'month'
  },
  'enterprise': {
    limit: 1000000,
    period: 'month'
  }
};

class ApiKeyManager {
  private apiKeys: ApiKey[] = [];
  private rateLimits: Map<string, RateLimitInfo> = new Map();
  private tenantQuotas: Map<string, { used: number; limit: number; resetTime: string }> = new Map();

  constructor() {
    // Initialize with mock data
    this.apiKeys = [...MOCK_API_KEYS];
    
    // Initialize rate limits
    this.apiKeys.forEach(key => {
      this.rateLimits.set(key.id, {
        keyId: key.id,
        requestsThisHour: Math.floor(Math.random() * key.rateLimit * 0.3),
        resetTime: new Date(Date.now() + 3600000).toISOString(),
        quotaUsed: Math.floor(Math.random() * 5000),
        quotaLimit: key.rateLimit
      });
    });
  }

  // Get all API keys for a tenant
  async getApiKeys(tenantId: string): Promise<ApiKey[]> {
    return this.apiKeys.filter(key => key.tenantId === tenantId);
  }

  // Get a specific API key by ID
  async getApiKey(keyId: string): Promise<ApiKey | null> {
    return this.apiKeys.find(key => key.id === keyId) || null;
  }

  // Create a new API key
  async createApiKey(tenantId: string, data: Omit<ApiKey, 'id' | 'key' | 'createdAt' | 'lastUsed' | 'status' | 'tenantId'>): Promise<ApiKey> {
    const newKey: ApiKey = {
      id: `ak_${Math.random().toString(36).substr(2, 9)}`,
      key: `rq_${data.environment}_${Math.random().toString(36).substr(2, 32)}`,
      createdAt: new Date().toISOString(),
      lastUsed: 'Never',
      status: 'active',
      tenantId,
      ...data
    };

    this.apiKeys.push(newKey);
    
    // Initialize rate limit tracking
    this.rateLimits.set(newKey.id, {
      keyId: newKey.id,
      requestsThisHour: 0,
      resetTime: new Date(Date.now() + 3600000).toISOString(),
      quotaUsed: 0,
      quotaLimit: newKey.rateLimit
    });

    return newKey;
  }

  // Update an existing API key
  async updateApiKey(keyId: string, updates: Partial<ApiKey>): Promise<ApiKey | null> {
    const index = this.apiKeys.findIndex(key => key.id === keyId);
    if (index === -1) return null;

    this.apiKeys[index] = { ...this.apiKeys[index], ...updates };
    return this.apiKeys[index];
  }

  // Delete an API key
  async deleteApiKey(keyId: string): Promise<boolean> {
    const index = this.apiKeys.findIndex(key => key.id === keyId);
    if (index === -1) return false;

    this.apiKeys.splice(index, 1);
    this.rateLimits.delete(keyId);
    return true;
  }

  // Check if an API key is valid and active
  async validateApiKey(key: string): Promise<{ valid: boolean; keyData?: ApiKey }> {
    const apiKey = this.apiKeys.find(k => k.key === key);
    
    if (!apiKey) {
      return { valid: false };
    }

    // Check if key is active
    if (apiKey.status !== 'active') {
      return { valid: false };
    }

    // Check if key has expired
    if (apiKey.expiresAt && new Date(apiKey.expiresAt) < new Date()) {
      // Auto-expire the key
      await this.updateApiKey(apiKey.id, { status: 'expired' });
      return { valid: false };
    }

    // Update last used time
    await this.updateApiKey(apiKey.id, { lastUsed: new Date().toISOString() });

    return { valid: true, keyData: apiKey };
  }

  // Check rate limit for an API key
  async checkRateLimit(keyId: string): Promise<{ allowed: boolean; remaining: number; resetTime: string }> {
    const rateLimit = this.rateLimits.get(keyId);
    if (!rateLimit) {
      return { allowed: false, remaining: 0, resetTime: new Date().toISOString() };
    }

    // Check if we need to reset the hourly counter
    if (new Date(rateLimit.resetTime) < new Date()) {
      rateLimit.requestsThisHour = 0;
      rateLimit.resetTime = new Date(Date.now() + 3600000).toISOString();
    }

    const apiKey = this.apiKeys.find(key => key.id === keyId);
    if (!apiKey) {
      return { allowed: false, remaining: 0, resetTime: new Date().toISOString() };
    }

    const allowed = rateLimit.requestsThisHour < apiKey.rateLimit;
    const remaining = Math.max(0, apiKey.rateLimit - rateLimit.requestsThisHour);

    return {
      allowed,
      remaining,
      resetTime: rateLimit.resetTime
    };
  }

  // Increment request count for rate limiting
  async incrementRequestCount(keyId: string): Promise<void> {
    const rateLimit = this.rateLimits.get(keyId);
    if (rateLimit) {
      rateLimit.requestsThisHour += 1;
    }
  }

  // Get rate limit info for a key
  async getRateLimitInfo(keyId: string): Promise<RateLimitInfo | null> {
    return this.rateLimits.get(keyId) || null;
  }

  // Get tenant quota info
  async getTenantQuota(tenantId: string, tier: string): Promise<{ used: number; limit: number; resetTime: string }> {
    // In a real implementation, this would be stored per tenant
    // For demo, we'll use a simple approach
    const quotaConfig = QUOTA_CONFIG[tier] || QUOTA_CONFIG['free'];
    
    // Initialize if not exists
    if (!this.tenantQuotas.has(tenantId)) {
      this.tenantQuotas.set(tenantId, {
        used: 0,
        limit: quotaConfig.limit,
        resetTime: new Date(new Date().setMonth(new Date().getMonth() + 1)).toISOString()
      });
    }

    return this.tenantQuotas.get(tenantId)!;
  }

  // Check if tenant is within quota
  async checkTenantQuota(tenantId: string, tier: string): Promise<{ withinQuota: boolean; used: number; limit: number }> {
    const quota = await this.getTenantQuota(tenantId, tier);
    return {
      withinQuota: quota.used < quota.limit,
      used: quota.used,
      limit: quota.limit
    };
  }

  // Increment tenant quota usage
  async incrementTenantQuota(tenantId: string, amount: number = 1): Promise<void> {
    const quota = this.tenantQuotas.get(tenantId);
    if (quota) {
      quota.used += amount;
    }
  }

  // Generate a secure API key
  generateSecureKey(length: number = 32): string {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
  }

  // Rotate an API key (generate new key while keeping metadata)
  async rotateApiKey(keyId: string): Promise<ApiKey | null> {
    const apiKey = await this.getApiKey(keyId);
    if (!apiKey) return null;

    const updatedKey = {
      ...apiKey,
      key: `rq_${apiKey.environment}_${this.generateSecureKey(32)}`,
      createdAt: new Date().toISOString()
    };

    await this.updateApiKey(keyId, updatedKey);
    return updatedKey;
  }
}

// Create singleton instance
const apiKeyManager = new ApiKeyManager();

// React hook for API key management
export function useApiKeyManager(tenantId: string) {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load API keys on mount
  useEffect(() => {
    const loadApiKeys = async () => {
      try {
        setLoading(true);
        const keys = await apiKeyManager.getApiKeys(tenantId);
        setApiKeys(keys);
      } catch (err) {
        setError('Failed to load API keys');
        console.error('Error loading API keys:', err);
      } finally {
        setLoading(false);
      }
    };

    if (tenantId) {
      loadApiKeys();
    }
  }, [tenantId]);

  // Create a new API key
  const createApiKey = async (data: Omit<ApiKey, 'id' | 'key' | 'createdAt' | 'lastUsed' | 'status' | 'tenantId'>) => {
    try {
      const newKey = await apiKeyManager.createApiKey(tenantId, data);
      setApiKeys(prev => [...prev, newKey]);
      return newKey;
    } catch (err) {
      setError('Failed to create API key');
      throw err;
    }
  };

  // Update an API key
  const updateApiKey = async (keyId: string, updates: Partial<ApiKey>) => {
    try {
      const updatedKey = await apiKeyManager.updateApiKey(keyId, updates);
      if (updatedKey) {
        setApiKeys(prev => prev.map(key => key.id === keyId ? updatedKey : key));
      }
      return updatedKey;
    } catch (err) {
      setError('Failed to update API key');
      throw err;
    }
  };

  // Delete an API key
  const deleteApiKey = async (keyId: string) => {
    try {
      const success = await apiKeyManager.deleteApiKey(keyId);
      if (success) {
        setApiKeys(prev => prev.filter(key => key.id !== keyId));
      }
      return success;
    } catch (err) {
      setError('Failed to delete API key');
      throw err;
    }
  };

  // Rotate an API key
  const rotateApiKey = async (keyId: string) => {
    try {
      const rotatedKey = await apiKeyManager.rotateApiKey(keyId);
      if (rotatedKey) {
        setApiKeys(prev => prev.map(key => key.id === keyId ? rotatedKey : key));
      }
      return rotatedKey;
    } catch (err) {
      setError('Failed to rotate API key');
      throw err;
    }
  };

  // Validate an API key
  const validateApiKey = async (key: string) => {
    return await apiKeyManager.validateApiKey(key);
  };

  // Get rate limit info
  const getRateLimitInfo = async (keyId: string) => {
    return await apiKeyManager.getRateLimitInfo(keyId);
  };

  return {
    apiKeys,
    loading,
    error,
    createApiKey,
    updateApiKey,
    deleteApiKey,
    rotateApiKey,
    validateApiKey,
    getRateLimitInfo
  };
}

// Hook for rate limiting
export function useRateLimit(keyId: string) {
  const [rateLimitInfo, setRateLimitInfo] = useState<RateLimitInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadRateLimitInfo = async () => {
      try {
        setLoading(true);
        const info = await apiKeyManager.getRateLimitInfo(keyId);
        setRateLimitInfo(info);
      } catch (err) {
        console.error('Error loading rate limit info:', err);
      } finally {
        setLoading(false);
      }
    };

    if (keyId) {
      loadRateLimitInfo();
    }
  }, [keyId]);

  return {
    rateLimitInfo,
    loading
  };
}

// Hook for tenant quota
export function useTenantQuota(tenantId: string, tier: string) {
  const [quotaInfo, setQuotaInfo] = useState<{ used: number; limit: number; resetTime: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadQuotaInfo = async () => {
      try {
        setLoading(true);
        const info = await apiKeyManager.getTenantQuota(tenantId, tier);
        setQuotaInfo(info);
      } catch (err) {
        console.error('Error loading quota info:', err);
      } finally {
        setLoading(false);
      }
    };

    if (tenantId && tier) {
      loadQuotaInfo();
    }
  }, [tenantId, tier]);

  return {
    quotaInfo,
    loading
  };
}

// Export the manager for direct use if needed
export { apiKeyManager };

// Utility functions
export const formatApiKey = (key: string): string => {
  if (key.length <= 8) return key;
  return `${key.substring(0, 4)}...${key.substring(key.length - 4)}`;
};

export const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'bg-green-100 text-green-800';
    case 'inactive': return 'bg-gray-100 text-gray-800';
    case 'expired': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export const getEnvironmentColor = (environment: string) => {
  switch (environment) {
    case 'production': return 'bg-red-100 text-red-800';
    case 'staging': return 'bg-yellow-100 text-yellow-800';
    case 'development': return 'bg-blue-100 text-blue-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};