'use client';

import { useState, useEffect } from 'react';
import ApiKeyManagement from '@/components/ApiKeyManagement';
import UsageAnalytics from '@/components/UsageAnalytics';
import { motion } from 'framer-motion';
import { 
  KeyIcon,
  ChartBarIcon,
  CogIcon,
  BellIcon,
  UserIcon,
  CreditCardIcon,
  QuestionMarkCircleIcon,
  PlusIcon,
  EyeIcon,
  EyeSlashIcon,
  TrashIcon,
  DocumentDuplicateIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

// Mock data - in real app this would come from API
const mockApiKeys = [
  {
    id: 'ak_abc123',
    name: 'Production API Key',
    key: 'rq_live_1234567890abcdef',
    created: '2024-01-15',
    lastUsed: '2024-01-20',
    requests: 25847,
    status: 'active',
    permissions: ['vault:read', 'vault:write', 'analytics:read']
  },
  {
    id: 'ak_def456',
    name: 'Development Testing',
    key: 'rq_test_abcdef1234567890',
    created: '2024-01-10',
    lastUsed: '2024-01-19',
    requests: 1256,
    status: 'active',
    permissions: ['vault:read', 'vault:write']
  }
];

const mockUsageStats = {
  currentMonth: {
    requests: 27103,
    limit: 100000,
    percentage: 27.1
  },
  lastMonth: {
    requests: 45678,
    growth: -40.6
  },
  avgResponseTime: 145,
  errorRate: 0.12
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [apiKeys, setApiKeys] = useState(mockApiKeys);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [hiddenKeys, setHiddenKeys] = useState<Set<string>>(new Set());
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

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

  const deleteApiKey = (keyId: string) => {
    setApiKeys(prev => prev.filter(key => key.id !== keyId));
  };

  const navigation = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'api-keys', name: 'API Keys', icon: KeyIcon },
    { id: 'usage', name: 'Usage & Analytics', icon: ChartBarIcon },
    { id: 'billing', name: 'Billing', icon: CreditCardIcon },
    { id: 'settings', name: 'Settings', icon: CogIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">ReliQuary Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600">
                <BellIcon className="h-6 w-6" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <UserIcon className="h-5 w-5 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700">John Doe</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex">
          {/* Sidebar Navigation */}
          <div className="w-64 mr-8">
            <nav className="space-y-1">
              {navigation.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {activeTab === 'overview' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard Overview</h2>
                
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center">
                      <ChartBarIcon className="h-8 w-8 text-blue-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">This Month</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {mockUsageStats.currentMonth.requests.toLocaleString()}
                        </p>
                        <p className="text-sm text-gray-500">API Requests</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center">
                      <KeyIcon className="h-8 w-8 text-green-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">API Keys</p>
                        <p className="text-2xl font-bold text-gray-900">{apiKeys.length}</p>
                        <p className="text-sm text-gray-500">Active Keys</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                        <span className="text-yellow-600 font-bold text-sm">⚡</span>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Avg Response</p>
                        <p className="text-2xl font-bold text-gray-900">{mockUsageStats.avgResponseTime}ms</p>
                        <p className="text-sm text-gray-500">Response Time</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-red-100 rounded-lg flex items-center justify-center">
                        <span className="text-red-600 font-bold text-sm">!</span>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Error Rate</p>
                        <p className="text-2xl font-bold text-gray-900">{mockUsageStats.errorRate}%</p>
                        <p className="text-sm text-gray-500">Last 30 Days</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Usage Progress */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Usage</h3>
                  <div className="mb-2 flex justify-between text-sm">
                    <span className="text-gray-600">
                      {mockUsageStats.currentMonth.requests.toLocaleString()} / {mockUsageStats.currentMonth.limit.toLocaleString()} requests
                    </span>
                    <span className="text-gray-600">{mockUsageStats.currentMonth.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${mockUsageStats.currentMonth.percentage}%` }}
                    ></div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent API Activity</h3>
                  <div className="space-y-3">
                    {apiKeys.map((key) => (
                      <div key={key.id} className="flex items-center justify-between py-2">
                        <div className="flex items-center space-x-3">
                          <KeyIcon className="h-5 w-5 text-gray-400" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{key.name}</p>
                            <p className="text-xs text-gray-500">Last used: {key.lastUsed}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">{key.requests.toLocaleString()}</p>
                          <p className="text-xs text-gray-500">requests</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'api-keys' && (
              <ApiKeyManagement />
            )}

            {activeTab === 'usage' && (
              <UsageAnalytics />
            )}

            {activeTab === 'billing' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-3xl font-bold text-gray-900 mb-8">Billing & Subscription</h2>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-gray-600">Billing management coming soon...</p>
                </div>
              </motion.div>
            )}

            {activeTab === 'settings' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-3xl font-bold text-gray-900 mb-8">Account Settings</h2>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-gray-600">Account settings coming soon...</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Create API Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New API Key</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Production API Key"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Permissions
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">vault:read</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">vault:write</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">analytics:read</span>
                  </label>
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-primary"
              >
                Create Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}