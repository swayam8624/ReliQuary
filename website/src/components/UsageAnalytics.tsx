'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  GlobeAltIcon,
  ServerIcon,
  KeyIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface UsageMetric {
  label: string;
  value: string;
  trend: number;
  color: 'green' | 'red' | 'blue' | 'yellow';
  icon: React.ComponentType<any>;
}

interface ApiEndpointUsage {
  endpoint: string;
  requests: number;
  errors: number;
  avgResponseTime: number;
  status: 'healthy' | 'warning' | 'error';
}

interface UsageOverTime {
  date: string;
  requests: number;
  errors: number;
  responseTime: number;
}

const mockUsageMetrics: UsageMetric[] = [
  {
    label: 'Total Requests',
    value: '127,439',
    trend: 15.2,
    color: 'blue',
    icon: ChartBarIcon
  },
  {
    label: 'Avg Response Time',
    value: '145ms',
    trend: -8.1,
    color: 'green',
    icon: ClockIcon
  },
  {
    label: 'Error Rate',
    value: '0.12%',
    trend: -25.4,
    color: 'green',
    icon: ExclamationTriangleIcon
  },
  {
    label: 'Success Rate',
    value: '99.88%',
    trend: 0.3,
    color: 'green',
    icon: CheckCircleIcon
  }
];

const mockEndpointUsage: ApiEndpointUsage[] = [
  {
    endpoint: '/vault/store',
    requests: 45672,
    errors: 23,
    avgResponseTime: 167,
    status: 'healthy'
  },
  {
    endpoint: '/vault/retrieve',
    requests: 38951,
    errors: 12,
    avgResponseTime: 142,
    status: 'healthy'
  },
  {
    endpoint: '/auth/login',
    requests: 12847,
    errors: 45,
    avgResponseTime: 89,
    status: 'warning'
  },
  {
    endpoint: '/vault/delete',
    requests: 8932,
    errors: 3,
    avgResponseTime: 134,
    status: 'healthy'
  },
  {
    endpoint: '/analytics/usage',
    requests: 5642,
    errors: 0,
    avgResponseTime: 256,
    status: 'healthy'
  }
];

const mockUsageOverTime: UsageOverTime[] = [
  { date: '2024-01-15', requests: 8547, errors: 12, responseTime: 152 },
  { date: '2024-01-16', requests: 9234, errors: 8, responseTime: 148 },
  { date: '2024-01-17', requests: 7892, errors: 15, responseTime: 165 },
  { date: '2024-01-18', requests: 10567, errors: 7, responseTime: 139 },
  { date: '2024-01-19', requests: 11234, errors: 9, responseTime: 145 },
  { date: '2024-01-20', requests: 12890, errors: 6, responseTime: 141 },
  { date: '2024-01-21', requests: 9876, errors: 11, responseTime: 156 }
];

export default function UsageAnalytics() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [selectedMetric, setSelectedMetric] = useState<'requests' | 'errors' | 'responseTime'>('requests');
  const [showRawData, setShowRawData] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <ArrowTrendingUpIcon className="h-4 w-4 text-green-600" />;
    } else if (trend < 0) {
      return <ArrowTrendingDownIcon className="h-4 w-4 text-red-600" />;
    }
    return null;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Usage Analytics</h2>
          <p className="text-gray-600 mt-1">Monitor your API usage, performance, and trends</p>
        </div>
        
        {/* Time Range Selector */}
        <div className="flex items-center space-x-4">
          <div className="flex bg-gray-100 rounded-lg p-1">
            {(['7d', '30d', '90d', '1y'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                  timeRange === range
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {range === '7d' && 'Last 7 days'}
                {range === '30d' && 'Last 30 days'}
                {range === '90d' && 'Last 90 days'}
                {range === '1y' && 'Last year'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {mockUsageMetrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg ${
                metric.color === 'blue' ? 'bg-blue-100' :
                metric.color === 'green' ? 'bg-green-100' :
                metric.color === 'red' ? 'bg-red-100' :
                'bg-yellow-100'
              }`}>
                <metric.icon className={`h-6 w-6 ${
                  metric.color === 'blue' ? 'text-blue-600' :
                  metric.color === 'green' ? 'text-green-600' :
                  metric.color === 'red' ? 'text-red-600' :
                  'text-yellow-600'
                }`} />
              </div>
              {getTrendIcon(metric.trend)}
            </div>
            
            <div>
              <p className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</p>
              <p className="text-sm font-medium text-gray-600 mb-2">{metric.label}</p>
              <div className="flex items-center text-sm">
                <span className={`${metric.trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.trend > 0 ? '+' : ''}{metric.trend}%
                </span>
                <span className="text-gray-500 ml-1">vs last period</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Usage Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Usage Over Time</h3>
          
          {/* Metric Selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setSelectedMetric('requests')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                selectedMetric === 'requests'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Requests
            </button>
            <button
              onClick={() => setSelectedMetric('errors')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                selectedMetric === 'errors'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Errors
            </button>
            <button
              onClick={() => setSelectedMetric('responseTime')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                selectedMetric === 'responseTime'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Response Time
            </button>
          </div>
        </div>

        {/* Simple Chart Visualization */}
        <div className="space-y-3">
          {mockUsageOverTime.map((data, index) => {
            const maxValue = Math.max(...mockUsageOverTime.map(d => 
              selectedMetric === 'requests' ? d.requests :
              selectedMetric === 'errors' ? d.errors :
              d.responseTime
            ));
            
            const value = selectedMetric === 'requests' ? data.requests :
                         selectedMetric === 'errors' ? data.errors :
                         data.responseTime;
            
            const percentage = (value / maxValue) * 100;
            
            return (
              <div key={data.date} className="flex items-center space-x-4">
                <div className="w-20 text-sm text-gray-600">
                  {new Date(data.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-3 relative">
                  <div 
                    className={`h-3 rounded-full transition-all duration-500 ${
                      selectedMetric === 'requests' ? 'bg-blue-500' :
                      selectedMetric === 'errors' ? 'bg-red-500' :
                      'bg-yellow-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
                <div className="w-16 text-sm text-gray-900 font-medium text-right">
                  {selectedMetric === 'responseTime' ? `${value}ms` : formatNumber(value)}
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Endpoint Usage */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">API Endpoint Usage</h3>
          <button
            onClick={() => setShowRawData(!showRawData)}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <EyeIcon className="h-4 w-4" />
            <span>{showRawData ? 'Hide' : 'Show'} Raw Data</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Endpoint</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Requests</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Errors</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Avg Response</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {mockEndpointUsage.map((endpoint, index) => (
                <motion.tr
                  key={endpoint.endpoint}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="border-b border-gray-100 hover:bg-gray-50"
                >
                  <td className="py-3 px-4">
                    <code className="text-sm font-mono text-gray-900">{endpoint.endpoint}</code>
                  </td>
                  <td className="py-3 px-4 font-medium text-gray-900">
                    {endpoint.requests.toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`text-sm ${endpoint.errors > 20 ? 'text-red-600' : 'text-gray-600'}`}>
                      {endpoint.errors}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {endpoint.avgResponseTime}ms
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(endpoint.status)}`}>
                      {endpoint.status}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {showRawData && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6 pt-6 border-t border-gray-200"
          >
            <h4 className="text-sm font-medium text-gray-700 mb-3">Raw Usage Data (JSON)</h4>
            <pre className="bg-gray-50 rounded-lg p-4 text-xs overflow-x-auto">
              {JSON.stringify(mockEndpointUsage, null, 2)}
            </pre>
          </motion.div>
        )}
      </motion.div>

      {/* Geographic Distribution */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Geographic Distribution</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { country: 'United States', requests: 45672, percentage: 35.8 },
            { country: 'Germany', requests: 23456, percentage: 18.4 },
            { country: 'United Kingdom', requests: 18934, percentage: 14.8 },
            { country: 'Canada', requests: 12847, percentage: 10.1 },
            { country: 'France', requests: 9876, percentage: 7.7 },
            { country: 'Other', requests: 16654, percentage: 13.2 }
          ].map((geo, index) => (
            <div key={geo.country} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <GlobeAltIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{geo.country}</p>
                  <p className="text-xs text-gray-500">{geo.requests.toLocaleString()} requests</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-gray-900">{geo.percentage}%</p>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ width: `${geo.percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}