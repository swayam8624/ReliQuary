'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  CreditCardIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ReceiptPercentIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

interface BillingPlan {
  id: string;
  name: string;
  price: number;
  period: 'month' | 'year';
  features: string[];
  limitations: string[];
  current: boolean;
  description: string;
}

interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'overdue';
  description: string;
}

interface UsageMetric {
  label: string;
  value: string;
  trend: number;
  color: 'green' | 'red' | 'blue' | 'yellow';
  icon: React.ComponentType<any>;
}

const BILLING_PLANS: BillingPlan[] = [
  {
    id: 'free',
    name: 'Developer',
    price: 0,
    period: 'month',
    features: [
      '1,000 API calls/month',
      'Basic cryptographic operations',
      'Standard algorithms (AES, RSA)',
      'Community support',
      'Self-hosting allowed'
    ],
    limitations: [
      'No advanced features',
      'No priority support',
      'No enterprise integrations'
    ],
    current: false,
    description: 'Perfect for developers and small projects'
  },
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    period: 'month',
    features: [
      '10,000 API calls/month',
      'All cryptographic features',
      'Post-quantum algorithms',
      'Multi-agent consensus',
      'Email support',
      'Basic analytics'
    ],
    limitations: [
      'No zero-knowledge proofs',
      'No custom deployment',
      'No dedicated support'
    ],
    current: true,
    description: 'For growing teams and production workloads'
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 499,
    period: 'month',
    features: [
      '100,000 API calls/month',
      'Advanced features (ZK proofs)',
      'Threshold cryptography',
      'SSO integration',
      'Priority email support',
      'Advanced analytics',
      'Custom dashboards'
    ],
    limitations: [
      'No custom deployment',
      'No dedicated infrastructure'
    ],
    current: false,
    description: 'For professional teams and growing businesses'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 1999,
    period: 'month',
    features: [
      'Unlimited API calls',
      'All features included',
      'Custom deployment options',
      'Dedicated support manager',
      'Professional services',
      'Custom SLA (up to 99.99%)',
      'On-premise deployment'
    ],
    limitations: [],
    current: false,
    description: 'For large organizations with advanced needs'
  }
];

const mockInvoices: Invoice[] = [
  {
    id: 'inv_001',
    date: '2024-01-01',
    amount: 99.00,
    status: 'paid',
    description: 'Starter Plan - January 2024'
  },
  {
    id: 'inv_002',
    date: '2023-12-01',
    amount: 99.00,
    status: 'paid',
    description: 'Starter Plan - December 2023'
  },
  {
    id: 'inv_003',
    date: '2023-11-01',
    amount: 99.00,
    status: 'paid',
    description: 'Starter Plan - November 2023'
  }
];

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

export default function BillingDashboard() {
  const [selectedPlan, setSelectedPlan] = useState<string>('starter');
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [billingPeriod, setBillingPeriod] = useState<'month' | 'year'>('month');
  const [invoices, setInvoices] = useState<Invoice[]>(mockInvoices);
  const [usageMetrics] = useState<UsageMetric[]>(mockUsageMetrics);

  const getCurrentPlan = () => {
    return BILLING_PLANS.find(plan => plan.current) || BILLING_PLANS[1];
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <ArrowTrendingUpIcon className="h-4 w-4 text-green-600" />;
    } else if (trend < 0) {
      return <ArrowTrendingDownIcon className="h-4 w-4 text-red-600" />;
    }
    return null;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleUpgradePlan = () => {
    // In a real implementation, this would call your backend API
    // to process the plan upgrade
    const currentPlan = getCurrentPlan();
    const newPlan = BILLING_PLANS.find(plan => plan.id === selectedPlan);
    
    if (newPlan && newPlan.id !== currentPlan.id) {
      // Update current plan
      const updatedPlans = BILLING_PLANS.map(plan => ({
        ...plan,
        current: plan.id === selectedPlan
      }));
      
      // For demo purposes, we'll just show a success message
      alert(`Plan upgraded to ${newPlan.name}!`);
      setShowUpgradeModal(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Billing & Usage</h2>
          <p className="text-gray-600 mt-1">Manage your subscription and monitor usage</p>
        </div>
        <button
          onClick={() => setShowUpgradeModal(true)}
          className="btn-primary"
        >
          Upgrade Plan
        </button>
      </div>

      {/* Current Plan */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Current Plan</h3>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
            Active
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-2xl font-bold text-gray-900">{getCurrentPlan().name}</h4>
            <p className="text-gray-600 mt-1">
              ${getCurrentPlan().price}/{getCurrentPlan().period}
            </p>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-600">Next billing date</p>
            <p className="font-medium text-gray-900">February 1, 2024</p>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Plan Features</h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {getCurrentPlan().features.map((feature, index) => (
              <li key={index} className="flex items-center text-sm text-gray-600">
                <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>
        </div>
      </motion.div>

      {/* Usage Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {usageMetrics.map((metric, index) => (
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
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button className="px-3 py-1 rounded-md text-sm font-medium bg-white text-gray-900 shadow-sm">
              Requests
            </button>
            <button className="px-3 py-1 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900">
              Errors
            </button>
            <button className="px-3 py-1 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900">
              Response Time
            </button>
          </div>
        </div>
        
        {/* Chart Visualization */}
        <div className="h-64 flex items-end space-x-2">
          {[65, 80, 45, 90, 75, 85, 70].map((height, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div 
                className="w-full bg-blue-500 rounded-t-lg transition-all duration-500 hover:bg-blue-600"
                style={{ height: `${height}%` }}
              ></div>
              <span className="text-xs text-gray-500 mt-2">
                {['M', 'T', 'W', 'T', 'F', 'S', 'S'][index]}
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Invoices */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Billing History</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Invoice</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Description</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Amount</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-900">
                    {invoice.id}
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {new Date(invoice.date).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {invoice.description}
                  </td>
                  <td className="py-3 px-4 font-medium text-gray-900">
                    ${invoice.amount.toFixed(2)}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(invoice.status)}`}>
                      {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Upgrade Plan Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Upgrade Your Plan</h3>
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="flex items-center mb-6">
              <span className="mr-4 text-gray-600">Billing Period:</span>
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setBillingPeriod('month')}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    billingPeriod === 'month'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Monthly
                </button>
                <button
                  onClick={() => setBillingPeriod('year')}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    billingPeriod === 'year'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Yearly <span className="text-green-600">(Save 20%)</span>
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {BILLING_PLANS.map((plan) => (
                <div
                  key={plan.id}
                  onClick={() => setSelectedPlan(plan.id)}
                  className={`border rounded-xl p-6 cursor-pointer transition-all ${
                    selectedPlan === plan.id
                      ? 'border-primary-500 ring-2 ring-primary-500 ring-opacity-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${plan.current ? 'relative bg-gradient-to-b from-white to-gray-50' : ''}`}
                >
                  {plan.current && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
                      Current Plan
                    </div>
                  )}
                  
                  <div className="mb-4">
                    <h4 className="text-lg font-bold text-gray-900">{plan.name}</h4>
                    <div className="mt-2">
                      <span className="text-3xl font-bold text-gray-900">
                        ${billingPeriod === 'year' ? plan.price * 10 : plan.price}
                      </span>
                      <span className="text-gray-600">/{billingPeriod === 'year' ? 'year' : 'month'}</span>
                    </div>
                    <p className="mt-2 text-sm text-gray-600">{plan.description}</p>
                  </div>
                  
                  <ul className="space-y-2 mb-6">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start">
                        <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                    {plan.limitations.map((limitation, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-gray-400 mr-2 mt-0.5">•</span>
                        <span className="text-sm text-gray-400">{limitation}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <button
                    className={`w-full py-2 px-4 rounded-lg font-medium ${
                      selectedPlan === plan.id
                        ? 'bg-primary-600 text-white'
                        : plan.current
                        ? 'bg-gray-200 text-gray-600'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                    disabled={plan.current}
                  >
                    {plan.current ? 'Current Plan' : 'Select Plan'}
                  </button>
                </div>
              ))}
            </div>
            
            <div className="flex justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpgradePlan}
                className="btn-primary"
              >
                Upgrade Plan
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}