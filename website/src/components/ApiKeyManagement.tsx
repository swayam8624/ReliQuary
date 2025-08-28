'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  KeyIcon,
  PlusIcon,
  EyeIcon,
  EyeSlashIcon,
  TrashIcon,
  DocumentDuplicateIcon,
  CheckIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  CogIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface ApiKey {
  id: string;
  name: string;
  key: string;
  created: string;
  lastUsed: string;
  requests: number;
  status: 'active' | 'inactive' | 'expired';
  permissions: string[];
  rateLimit: number;
  expiresAt?: string;
  allowedIps?: string[];
  environment: 'production' | 'development' | 'staging';
}

interface CreateKeyForm {
  name: string;
  permissions: string[];
  rateLimit: number;
  expiresAt: string;
  allowedIps: string;
  environment: 'production' | 'development' | 'staging';
}

const AVAILABLE_PERMISSIONS = [
  { id: 'vault:read', label: 'Vault Read', description: 'Read encrypted data from vault' },
  { id: 'vault:write', label: 'Vault Write', description: 'Store encrypted data in vault' },
  { id: 'vault:delete', label: 'Vault Delete', description: 'Delete data from vault' },
  { id: 'analytics:read', label: 'Analytics Read', description: 'Access usage analytics' },
  { id: 'keys:read', label: 'Keys Read', description: 'List API keys' },
  { id: 'keys:write', label: 'Keys Write', description: 'Create/modify API keys' },
  { id: 'billing:read', label: 'Billing Read', description: 'Access billing information' },
  { id: 'admin:full', label: 'Admin Full Access', description: 'Full administrative access' }
];

const RATE_LIMIT_PRESETS = [
  { value: 100, label: '100 requests/hour (Development)' },
  { value: 1000, label: '1,000 requests/hour (Testing)' },
  { value: 10000, label: '10,000 requests/hour (Production)' },
  { value: 100000, label: '100,000 requests/hour (Enterprise)' },
  { value: -1, label: 'Unlimited (Admin)' }
];

const mockApiKeys: ApiKey[] = [
  {
    id: 'ak_abc123',
    name: 'Production API Key',
    key: 'rq_live_1234567890abcdef1234567890abcdef',
    created: '2024-01-15',
    lastUsed: '2024-01-20T10:30:00Z',
    requests: 25847,
    status: 'active',
    permissions: ['vault:read', 'vault:write', 'analytics:read'],
    rateLimit: 10000,
    environment: 'production',
    allowedIps: ['203.0.113.1', '203.0.113.2']
  },
  {
    id: 'ak_def456',
    name: 'Development Testing',
    key: 'rq_test_abcdef1234567890abcdef1234567890',
    created: '2024-01-10',
    lastUsed: '2024-01-19T15:45:00Z',
    requests: 1256,
    status: 'active',
    permissions: ['vault:read', 'vault:write'],
    rateLimit: 1000,
    environment: 'development'
  },
  {
    id: 'ak_ghi789',
    name: 'Staging Environment',
    key: 'rq_staging_fedcba0987654321fedcba0987654321',
    created: '2024-01-05',
    lastUsed: '2024-01-18T09:15:00Z',
    requests: 5432,
    status: 'active',
    permissions: ['vault:read', 'vault:write', 'analytics:read'],
    rateLimit: 5000,
    environment: 'staging',
    expiresAt: '2024-06-01'
  }
];

export default function ApiKeyManagement() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>(mockApiKeys);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [hiddenKeys, setHiddenKeys] = useState<Set<string>>(new Set());
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [keyToDelete, setKeyToDelete] = useState<string | null>(null);
  const [createForm, setCreateForm] = useState<CreateKeyForm>({
    name: '',
    permissions: [],
    rateLimit: 1000,
    expiresAt: '',
    allowedIps: '',
    environment: 'development'
  });

  const toggleKeyVisibility = (keyId: string) => {
    const newHidden = new Set(hiddenKeys);
    if (newHidden.has(keyId)) {
      newHidden.delete(keyId);
    } else {
      newHidden.add(keyId);
    }
    setHiddenKeys(newHidden);
  };

  const copyApiKey = async (key: string) => {
    try {
      await navigator.clipboard.writeText(key);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const handleDeleteKey = (keyId: string) => {
    setKeyToDelete(keyId);
    setShowDeleteModal(true);
  };

  const confirmDeleteKey = () => {
    if (keyToDelete) {
      setApiKeys(prev => prev.filter(key => key.id !== keyToDelete));
      setKeyToDelete(null);
      setShowDeleteModal(false);
    }
  };

  const handleCreateKey = () => {
    const newKey: ApiKey = {
      id: `ak_${Math.random().toString(36).substr(2, 9)}`,
      name: createForm.name,
      key: `rq_${createForm.environment}_${Math.random().toString(36).substr(2, 32)}`,
      created: new Date().toISOString().split('T')[0],
      lastUsed: 'Never',
      requests: 0,
      status: 'active',
      permissions: createForm.permissions,
      rateLimit: createForm.rateLimit,
      environment: createForm.environment,
      expiresAt: createForm.expiresAt || undefined,
      allowedIps: createForm.allowedIps ? createForm.allowedIps.split(',').map(ip => ip.trim()) : undefined
    };

    setApiKeys(prev => [...prev, newKey]);
    setShowCreateModal(false);
    setCreateForm({
      name: '',
      permissions: [],
      rateLimit: 1000,
      expiresAt: '',
      allowedIps: '',
      environment: 'development'
    });
  };

  const togglePermission = (permission: string) => {
    setCreateForm(prev => ({
      ...prev,
      permissions: prev.permissions.includes(permission)
        ? prev.permissions.filter(p => p !== permission)
        : [...prev.permissions, permission]
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700';
      case 'inactive': return 'bg-gray-100 text-gray-700';
      case 'expired': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getEnvironmentColor = (environment: string) => {
    switch (environment) {
      case 'production': return 'bg-red-100 text-red-700';
      case 'staging': return 'bg-yellow-100 text-yellow-700';
      case 'development': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const formatDateTime = (dateString: string) => {
    if (dateString === 'Never') return dateString;
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">API Keys</h2>
          <p className="text-gray-600 mt-1">Manage your API keys and access permissions</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Create New Key
        </button>
      </div>

      {/* API Keys List */}
      <div className="space-y-4">
        {apiKeys.map((key) => (
          <motion.div
            key={key.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{key.name}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(key.status)}`}>
                    {key.status}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEnvironmentColor(key.environment)}`}>
                    {key.environment}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Created: {formatDate(key.created)}</span>
                  <span>Last used: {formatDateTime(key.lastUsed)}</span>
                  {key.expiresAt && (
                    <span className="flex items-center text-yellow-600">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      Expires: {formatDate(key.expiresAt)}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDeleteKey(key.id)}
                  className="p-2 text-red-400 hover:text-red-600 transition-colors"
                  title="Delete key"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* API Key Display */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div className="flex items-center space-x-2">
                <code className="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm font-mono overflow-hidden">
                  {hiddenKeys.has(key.id) 
                    ? '••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••'
                    : key.key
                  }
                </code>
                <button
                  onClick={() => toggleKeyVisibility(key.id)}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  title={hiddenKeys.has(key.id) ? 'Show key' : 'Hide key'}
                >
                  {hiddenKeys.has(key.id) ? (
                    <EyeIcon className="h-4 w-4" />
                  ) : (
                    <EyeSlashIcon className="h-4 w-4" />
                  )}
                </button>
                <button
                  onClick={() => copyApiKey(key.key)}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Copy to clipboard"
                >
                  {copiedKey === key.key ? (
                    <CheckIcon className="h-4 w-4 text-green-600" />
                  ) : (
                    <DocumentDuplicateIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Key Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <ChartBarIcon className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Requests</p>
                    <p className="text-lg font-bold text-gray-900">{key.requests.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
                    <CogIcon className="h-4 w-4 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Rate Limit</p>
                    <p className="text-lg font-bold text-gray-900">
                      {key.rateLimit === -1 ? 'Unlimited' : `${key.rateLimit.toLocaleString()}/hr`}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                    <ShieldCheckIcon className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Permissions</p>
                    <p className="text-lg font-bold text-gray-900">{key.permissions.length}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Permissions */}
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Permissions</p>
              <div className="flex flex-wrap gap-2">
                {key.permissions.map((permission) => (
                  <span
                    key={permission}
                    className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full"
                  >
                    {permission}
                  </span>
                ))}
              </div>
            </div>

            {/* Security Info */}
            {key.allowedIps && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Allowed IP Addresses</p>
                <div className="flex items-center space-x-2">
                  <GlobeAltIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{key.allowedIps.join(', ')}</span>
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Create API Key Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Create New API Key</h3>
              
              <div className="space-y-6">
                {/* Basic Info */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Key Name *
                  </label>
                  <input
                    type="text"
                    value={createForm.name}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., Production API Key"
                  />
                </div>

                {/* Environment */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Environment *
                  </label>
                  <select
                    value={createForm.environment}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, environment: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="development">Development</option>
                    <option value="staging">Staging</option>
                    <option value="production">Production</option>
                  </select>
                </div>

                {/* Rate Limit */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rate Limit
                  </label>
                  <select
                    value={createForm.rateLimit}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, rateLimit: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {RATE_LIMIT_PRESETS.map((preset) => (
                      <option key={preset.value} value={preset.value}>
                        {preset.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Expiration */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expiration Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={createForm.expiresAt}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, expiresAt: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Allowed IPs */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Allowed IP Addresses (Optional)
                  </label>
                  <input
                    type="text"
                    value={createForm.allowedIps}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, allowedIps: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="203.0.113.1, 203.0.113.2"
                  />
                  <p className="text-xs text-gray-500 mt-1">Comma-separated list of IP addresses</p>
                </div>

                {/* Permissions */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Permissions *
                  </label>
                  <div className="space-y-3 max-h-40 overflow-y-auto">
                    {AVAILABLE_PERMISSIONS.map((permission) => (
                      <label key={permission.id} className="flex items-start">
                        <input
                          type="checkbox"
                          checked={createForm.permissions.includes(permission.id)}
                          onChange={() => togglePermission(permission.id)}
                          className="mt-1 mr-3"
                        />
                        <div>
                          <span className="text-sm font-medium text-gray-900">{permission.label}</span>
                          <p className="text-xs text-gray-500">{permission.description}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateKey}
                  disabled={!createForm.name || createForm.permissions.length === 0}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Key
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {showDeleteModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-xl p-6 w-full max-w-md"
            >
              <div className="flex items-center mb-4">
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Delete API Key</h3>
              </div>
              
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete this API key? This action cannot be undone and will immediately revoke access.
              </p>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDeleteKey}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete Key
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}