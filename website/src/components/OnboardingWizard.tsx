// Multi-Tenant Onboarding Wizard
// Comprehensive onboarding flow for new users and organizations

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BuildingOfficeIcon,
  UserIcon,
  CreditCardIcon,
  KeyIcon,
  CheckCircleIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
}

interface OrganizationData {
  name: string;
  domain: string;
  industry: string;
  size: string;
  useCase: string;
}

interface UserData {
  firstName: string;
  lastName: string;
  role: string;
  department: string;
}

interface BillingData {
  plan: 'free' | 'starter' | 'professional' | 'enterprise';
  paymentMethod: 'card' | 'invoice' | 'bank';
  cardNumber?: string;
  expiryDate?: string;
  cvv?: string;
}

interface ApiKeyData {
  name: string;
  permissions: string[];
  environment: 'development' | 'staging' | 'production';
}

const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'organization',
    title: 'Organization Details',
    description: 'Tell us about your organization',
    icon: BuildingOfficeIcon
  },
  {
    id: 'user',
    title: 'Your Profile',
    description: 'Set up your user profile',
    icon: UserIcon
  },
  {
    id: 'billing',
    title: 'Billing & Plan',
    description: 'Choose your subscription plan',
    icon: CreditCardIcon
  },
  {
    id: 'apikey',
    title: 'API Access',
    description: 'Create your first API key',
    icon: KeyIcon
  },
  {
    id: 'complete',
    title: 'Get Started',
    description: 'You\'re all set!',
    icon: CheckCircleIcon
  }
];

const INDUSTRIES = [
  'Technology/Software',
  'Financial Services',
  'Healthcare',
  'Government',
  'Education',
  'E-commerce',
  'Gaming',
  'Manufacturing',
  'Energy/Utilities',
  'Telecommunications',
  'Media/Entertainment',
  'Other'
];

const COMPANY_SIZES = [
  '1-10 employees',
  '11-50 employees',
  '51-200 employees',
  '201-500 employees',
  '501-1000 employees',
  '1000+ employees'
];

const USE_CASES = [
  'Data Protection',
  'Compliance',
  'Secure Storage',
  'Identity Management',
  'API Security',
  'Multi-Party Computation',
  'Zero-Knowledge Proofs',
  'Post-Quantum Cryptography',
  'Other'
];

const USER_ROLES = [
  'Developer',
  'Security Engineer',
  'DevOps Engineer',
  'System Administrator',
  'CTO/Technical Lead',
  'Product Manager',
  'Other'
];

const DEPARTMENTS = [
  'Engineering',
  'Security',
  'DevOps',
  'Product',
  'IT Operations',
  'Research & Development',
  'Other'
];

const PLANS = [
  {
    id: 'free',
    name: 'Developer',
    price: '$0',
    period: 'forever',
    description: 'Perfect for developers and small projects',
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
    popular: false
  },
  {
    id: 'starter',
    name: 'Starter',
    price: '$99',
    period: 'per month',
    description: 'For growing teams and production workloads',
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
    popular: false
  },
  {
    id: 'professional',
    name: 'Professional',
    price: '$499',
    period: 'per month',
    description: 'For professional teams and growing businesses',
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
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: '$1,999',
    period: 'per month',
    description: 'For large organizations with advanced needs',
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
    popular: false
  }
];

export default function OnboardingWizard() {
  const [currentStep, setCurrentStep] = useState(0);
  const [organizationData, setOrganizationData] = useState<OrganizationData>({
    name: '',
    domain: '',
    industry: '',
    size: '',
    useCase: ''
  });
  const [userData, setUserData] = useState<UserData>({
    firstName: '',
    lastName: '',
    role: '',
    department: ''
  });
  const [billingData, setBillingData] = useState<BillingData>({
    plan: 'starter',
    paymentMethod: 'card'
  });
  const [apiKeyData, setApiKeyData] = useState<ApiKeyData>({
    name: 'Production API Key',
    permissions: ['vault:read', 'vault:write'],
    environment: 'production'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleNext = () => {
    if (currentStep < ONBOARDING_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real implementation, this would call your backend API
      // to create the organization, user, and initial setup
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSuccess(true);
      
      // Redirect to dashboard after success
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 3000);
    } catch (err) {
      setError('Failed to complete onboarding. Please try again.');
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Organization
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Name *
              </label>
              <input
                type="text"
                value={organizationData.name}
                onChange={(e) => setOrganizationData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Acme Corporation"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Domain
              </label>
              <input
                type="text"
                value={organizationData.domain}
                onChange={(e) => setOrganizationData(prev => ({ ...prev, domain: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="acme.com"
              />
              <p className="mt-1 text-sm text-gray-500">
                This will be your custom subdomain (e.g., acme.reliquary.io)
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry *
                </label>
                <select
                  value={organizationData.industry}
                  onChange={(e) => setOrganizationData(prev => ({ ...prev, industry: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                >
                  <option value="">Select industry</option>
                  {INDUSTRIES.map(industry => (
                    <option key={industry} value={industry}>{industry}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Size *
                </label>
                <select
                  value={organizationData.size}
                  onChange={(e) => setOrganizationData(prev => ({ ...prev, size: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                >
                  <option value="">Select size</option>
                  {COMPANY_SIZES.map(size => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Primary Use Case *
              </label>
              <select
                value={organizationData.useCase}
                onChange={(e) => setOrganizationData(prev => ({ ...prev, useCase: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                required
              >
                <option value="">Select use case</option>
                {USE_CASES.map(useCase => (
                  <option key={useCase} value={useCase}>{useCase}</option>
                ))}
              </select>
            </div>
          </div>
        );
      
      case 1: // User Profile
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  value={userData.firstName}
                  onChange={(e) => setUserData(prev => ({ ...prev, firstName: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="John"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  value={userData.lastName}
                  onChange={(e) => setUserData(prev => ({ ...prev, lastName: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Doe"
                  required
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role *
                </label>
                <select
                  value={userData.role}
                  onChange={(e) => setUserData(prev => ({ ...prev, role: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                >
                  <option value="">Select role</option>
                  {USER_ROLES.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Department *
                </label>
                <select
                  value={userData.department}
                  onChange={(e) => setUserData(prev => ({ ...prev, department: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                >
                  <option value="">Select department</option>
                  {DEPARTMENTS.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                <p className="text-sm text-blue-700">
                  You'll be set up as the organization administrator. You can invite team members later.
                </p>
              </div>
            </div>
          </div>
        );
      
      case 2: // Billing & Plan
        return (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose Your Plan</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {PLANS.map((plan) => (
                  <div
                    key={plan.id}
                    onClick={() => setBillingData(prev => ({ ...prev, plan: plan.id as any }))}
                    className={`border rounded-xl p-6 cursor-pointer transition-all ${
                      billingData.plan === plan.id
                        ? 'border-primary-500 ring-2 ring-primary-500 ring-opacity-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${plan.popular ? 'relative bg-gradient-to-b from-white to-gray-50' : ''}`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
                        Most Popular
                      </div>
                    )}
                    
                    <div className="mb-4">
                      <h4 className="text-lg font-bold text-gray-900">{plan.name}</h4>
                      <div className="mt-2">
                        <span className="text-3xl font-bold text-gray-900">{plan.price}</span>
                        <span className="text-gray-600">/{plan.period}</span>
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
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Method</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setBillingData(prev => ({ ...prev, paymentMethod: 'card' }))}
                  className={`p-4 border rounded-lg text-center ${
                    billingData.paymentMethod === 'card'
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <CreditCardIcon className="h-6 w-6 mx-auto text-gray-600 mb-2" />
                  <span className="text-sm font-medium">Credit Card</span>
                </button>
                
                <button
                  onClick={() => setBillingData(prev => ({ ...prev, paymentMethod: 'invoice' }))}
                  className={`p-4 border rounded-lg text-center ${
                    billingData.paymentMethod === 'invoice'
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <BuildingOfficeIcon className="h-6 w-6 mx-auto text-gray-600 mb-2" />
                  <span className="text-sm font-medium">Invoice</span>
                </button>
                
                <button
                  onClick={() => setBillingData(prev => ({ ...prev, paymentMethod: 'bank' }))}
                  className={`p-4 border rounded-lg text-center ${
                    billingData.paymentMethod === 'bank'
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <BuildingOfficeIcon className="h-6 w-6 mx-auto text-gray-600 mb-2" />
                  <span className="text-sm font-medium">Bank Transfer</span>
                </button>
              </div>
              
              {billingData.paymentMethod === 'card' && (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Card Number
                    </label>
                    <input
                      type="text"
                      placeholder="1234 5678 9012 3456"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expiry Date
                      </label>
                      <input
                        type="text"
                        placeholder="MM/YY"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CVV
                      </label>
                      <input
                        type="text"
                        placeholder="123"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      
      case 3: // API Key
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key Name *
              </label>
              <input
                type="text"
                value={apiKeyData.name}
                onChange={(e) => setApiKeyData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Production API Key"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Environment
              </label>
              <div className="grid grid-cols-3 gap-4">
                {(['development', 'staging', 'production'] as const).map(env => (
                  <button
                    key={env}
                    onClick={() => setApiKeyData(prev => ({ ...prev, environment: env }))}
                    className={`p-3 border rounded-lg text-center capitalize ${
                      apiKeyData.environment === env
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {env}
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Permissions
              </label>
              <div className="space-y-3">
                {[
                  { id: 'vault:read', label: 'Vault Read', description: 'Read encrypted data from vault' },
                  { id: 'vault:write', label: 'Vault Write', description: 'Store encrypted data in vault' },
                  { id: 'vault:delete', label: 'Vault Delete', description: 'Delete data from vault' },
                  { id: 'analytics:read', label: 'Analytics Read', description: 'Access usage analytics' },
                  { id: 'keys:read', label: 'Keys Read', description: 'List API keys' },
                  { id: 'keys:write', label: 'Keys Write', description: 'Create/modify API keys' }
                ].map(permission => (
                  <label key={permission.id} className="flex items-start">
                    <input
                      type="checkbox"
                      checked={apiKeyData.permissions.includes(permission.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setApiKeyData(prev => ({
                            ...prev,
                            permissions: [...prev.permissions, permission.id]
                          }));
                        } else {
                          setApiKeyData(prev => ({
                            ...prev,
                            permissions: prev.permissions.filter(p => p !== permission.id)
                          }));
                        }
                      }}
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
            
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                <div>
                  <p className="text-sm text-blue-700 font-medium mb-1">API Key Security</p>
                  <p className="text-sm text-blue-700">
                    Your API key will be generated after onboarding. Store it securely and never share it in client-side code.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 4: // Complete
        return (
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to ReliQuary!</h3>
            <p className="text-gray-600 mb-8">
              Your organization has been successfully set up. You're ready to start securing your data.
            </p>
            
            <div className="bg-gray-50 rounded-lg p-6 mb-8 text-left">
              <h4 className="font-semibold text-gray-900 mb-3">Next Steps</h4>
              <ul className="space-y-2">
                <li className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-sm">Explore the dashboard</span>
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-sm">Review your API key settings</span>
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-sm">Invite team members to your organization</span>
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-sm">Set up your first vault</span>
                </li>
              </ul>
            </div>
            
            <div className="text-sm text-gray-500">
              Redirecting to your dashboard...
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 0: // Organization
        return organizationData.name && organizationData.industry && organizationData.size && organizationData.useCase;
      case 1: // User
        return userData.firstName && userData.lastName && userData.role && userData.department;
      case 2: // Billing
        return true; // Plan selection is optional for now
      case 3: // API Key
        return apiKeyData.name && apiKeyData.permissions.length > 0;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white rounded-2xl shadow-xl overflow-hidden"
          >
            {/* Progress Bar */}
            <div className="px-8 pt-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {ONBOARDING_STEPS[currentStep].title}
                </h2>
                <span className="text-sm font-medium text-gray-500">
                  Step {currentStep + 1} of {ONBOARDING_STEPS.length}
                </span>
              </div>
              
              <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                  {ONBOARDING_STEPS.map((step, index) => (
                    <div key={step.id} className="flex items-center">
                      <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                        index <= currentStep 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-gray-200 text-gray-500'
                      }`}>
                        {index < currentStep ? (
                          <CheckCircleIcon className="h-5 w-5" />
                        ) : (
                          index + 1
                        )}
                      </div>
                      {index < ONBOARDING_STEPS.length - 1 && (
                        <div className={`h-1 w-16 mx-2 ${
                          index < currentStep ? 'bg-primary-600' : 'bg-gray-200'
                        }`} />
                      )}
                    </div>
                  ))}
                </div>
                
                <p className="text-gray-600">
                  {ONBOARDING_STEPS[currentStep].description}
                </p>
              </div>
            </div>
            
            {/* Step Content */}
            <div className="px-8 pb-8">
              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
                  <InformationCircleIcon className="h-5 w-5 text-red-600 mr-3" />
                  <span className="text-red-700 text-sm">{error}</span>
                </div>
              )}
              
              {renderStepContent()}
            </div>
            
            {/* Navigation */}
            <div className="px-8 py-6 bg-gray-50 border-t border-gray-200">
              <div className="flex justify-between">
                <button
                  onClick={handlePrevious}
                  disabled={currentStep === 0}
                  className={`flex items-center px-4 py-2 rounded-lg font-medium ${
                    currentStep === 0
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <ArrowLeftIcon className="h-5 w-5 mr-2" />
                  Previous
                </button>
                
                {currentStep < ONBOARDING_STEPS.length - 1 ? (
                  <button
                    onClick={handleNext}
                    disabled={!isStepValid() || loading}
                    className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                    <ArrowRightIcon className="h-5 w-5 ml-2" />
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    disabled={!isStepValid() || loading || success}
                    className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Completing Setup...
                      </>
                    ) : success ? (
                      <>
                        <CheckCircleIcon className="h-5 w-5 mr-2" />
                        Redirecting...
                      </>
                    ) : (
                      <>
                        Complete Setup
                        <ArrowRightIcon className="h-5 w-5 ml-2" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}