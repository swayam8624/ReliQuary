'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  EyeIcon,
  EyeSlashIcon,
  ShieldCheckIcon,
  EnvelopeIcon,
  KeyIcon,
  BuildingOfficeIcon,
  UserIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowRightIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

interface AuthFormData {
  email: string;
  password: string;
  confirmPassword?: string;
  firstName?: string;
  lastName?: string;
  organization?: string;
  role?: string;
  agreeToTerms?: boolean;
}

interface AuthState {
  mode: 'login' | 'register' | 'forgot-password' | 'onboarding';
  loading: boolean;
  error: string | null;
  success: string | null;
}

const ORGANIZATION_TYPES = [
  'Technology/Software',
  'Financial Services',
  'Healthcare',
  'Government',
  'Education',
  'E-commerce',
  'Gaming',
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

export default function UserAuthentication() {
  const [authState, setAuthState] = useState<AuthState>({
    mode: 'login',
    loading: false,
    error: null,
    success: null
  });

  const [formData, setFormData] = useState<AuthFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    organization: '',
    role: '',
    agreeToTerms: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleInputChange = (field: keyof AuthFormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear errors when user starts typing
    if (authState.error) {
      setAuthState(prev => ({ ...prev, error: null }));
    }
  };

  const validateForm = () => {
    const { mode } = authState;
    const { email, password, confirmPassword, firstName, lastName, organization, agreeToTerms } = formData;

    if (!email || !email.includes('@')) {
      return 'Please enter a valid email address';
    }

    if (mode === 'forgot-password') {
      return null; // Only email needed for password reset
    }

    if (!password || password.length < 8) {
      return 'Password must be at least 8 characters long';
    }

    if (mode === 'register') {
      if (!firstName || !lastName) {
        return 'Please enter your first and last name';
      }

      if (!organization) {
        return 'Please enter your organization name';
      }

      if (password !== confirmPassword) {
        return 'Passwords do not match';
      }

      if (!agreeToTerms) {
        return 'Please agree to the Terms of Service and Privacy Policy';
      }
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setAuthState(prev => ({ ...prev, error: validationError }));
      return;
    }

    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const { mode } = authState;
      
      if (mode === 'login') {
        setAuthState(prev => ({ ...prev, success: 'Login successful! Redirecting to dashboard...' }));
        // Redirect to dashboard
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      } else if (mode === 'register') {
        setAuthState(prev => ({ ...prev, mode: 'onboarding', success: 'Account created successfully!' }));
      } else if (mode === 'forgot-password') {
        setAuthState(prev => ({ 
          ...prev, 
          success: 'Password reset instructions have been sent to your email.',
          mode: 'login'
        }));
      }
    } catch (error) {
      setAuthState(prev => ({ 
        ...prev, 
        error: 'An error occurred. Please try again.' 
      }));
    } finally {
      setAuthState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleCompleteOnboarding = async () => {
    setAuthState(prev => ({ ...prev, loading: true }));
    
    try {
      // Simulate onboarding completion
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setAuthState(prev => ({ 
        ...prev, 
        success: 'Onboarding completed! Welcome to ReliQuary!' 
      }));
      
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
    } catch (error) {
      setAuthState(prev => ({ 
        ...prev, 
        error: 'Failed to complete onboarding. Please try again.' 
      }));
    } finally {
      setAuthState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <AnimatePresence mode="wait">
          {authState.mode !== 'onboarding' && (
            <motion.div
              key={authState.mode}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-2xl shadow-xl p-8"
            >
              {/* Header */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-2xl mb-4">
                  <ShieldCheckIcon className="h-8 w-8 text-primary-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  {authState.mode === 'login' && 'Welcome Back'}
                  {authState.mode === 'register' && 'Create Account'}
                  {authState.mode === 'forgot-password' && 'Reset Password'}
                </h2>
                <p className="text-gray-600">
                  {authState.mode === 'login' && 'Sign in to your ReliQuary account'}
                  {authState.mode === 'register' && 'Join ReliQuary to secure your data'}
                  {authState.mode === 'forgot-password' && 'Enter your email to reset your password'}
                </p>
              </div>

              {/* Error/Success Messages */}
              {authState.error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center"
                >
                  <ExclamationCircleIcon className="h-5 w-5 text-red-600 mr-3" />
                  <span className="text-red-700 text-sm">{authState.error}</span>
                </motion.div>
              )}

              {authState.success && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center"
                >
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mr-3" />
                  <span className="text-green-700 text-sm">{authState.success}</span>
                </motion.div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <EnvelopeIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                      placeholder="your@email.com"
                      required
                    />
                  </div>
                </div>

                {/* Password (not for forgot password) */}
                {authState.mode !== 'forgot-password' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <KeyIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={(e) => handleInputChange('password', e.target.value)}
                        className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                        placeholder="Enter your password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword ? (
                          <EyeSlashIcon className="h-5 w-5" />
                        ) : (
                          <EyeIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Registration Fields */}
                {authState.mode === 'register' && (
                  <>
                    {/* Confirm Password */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Confirm Password
                      </label>
                      <div className="relative">
                        <KeyIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <input
                          type={showConfirmPassword ? 'text' : 'password'}
                          value={formData.confirmPassword}
                          onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                          className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                          placeholder="Confirm your password"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          {showConfirmPassword ? (
                            <EyeSlashIcon className="h-5 w-5" />
                          ) : (
                            <EyeIcon className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Name Fields */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          First Name
                        </label>
                        <div className="relative">
                          <UserIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                          <input
                            type="text"
                            value={formData.firstName}
                            onChange={(e) => handleInputChange('firstName', e.target.value)}
                            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                            placeholder="John"
                            required
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Last Name
                        </label>
                        <input
                          type="text"
                          value={formData.lastName}
                          onChange={(e) => handleInputChange('lastName', e.target.value)}
                          className="w-full pl-4 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                          placeholder="Doe"
                          required
                        />
                      </div>
                    </div>

                    {/* Organization */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Organization
                      </label>
                      <div className="relative">
                        <BuildingOfficeIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <input
                          type="text"
                          value={formData.organization}
                          onChange={(e) => handleInputChange('organization', e.target.value)}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                          placeholder="Your Company"
                          required
                        />
                      </div>
                    </div>

                    {/* Terms Agreement */}
                    <div className="flex items-start">
                      <input
                        type="checkbox"
                        checked={formData.agreeToTerms}
                        onChange={(e) => handleInputChange('agreeToTerms', e.target.checked)}
                        className="mt-1 mr-3"
                        required
                      />
                      <label className="text-sm text-gray-600">
                        I agree to the{' '}
                        <a href="/terms" className="text-primary-600 hover:text-primary-700">
                          Terms of Service
                        </a>{' '}
                        and{' '}
                        <a href="/privacy" className="text-primary-600 hover:text-primary-700">
                          Privacy Policy
                        </a>
                      </label>
                    </div>
                  </>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={authState.loading}
                  className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {authState.loading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Processing...
                    </div>
                  ) : (
                    <>
                      {authState.mode === 'login' && 'Sign In'}
                      {authState.mode === 'register' && 'Create Account'}
                      {authState.mode === 'forgot-password' && 'Send Reset Link'}
                      <ArrowRightIcon className="h-5 w-5 ml-2" />
                    </>
                  )}
                </button>
              </form>

              {/* Footer Links */}
              <div className="mt-6 text-center">
                {authState.mode === 'login' && (
                  <div className="space-y-2">
                    <button
                      onClick={() => setAuthState(prev => ({ ...prev, mode: 'forgot-password' }))}
                      className="text-primary-600 hover:text-primary-700 text-sm"
                    >
                      Forgot your password?
                    </button>
                    <p className="text-gray-600 text-sm">
                      Don't have an account?{' '}
                      <button
                        onClick={() => setAuthState(prev => ({ ...prev, mode: 'register' }))}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        Sign up
                      </button>
                    </p>
                  </div>
                )}

                {authState.mode === 'register' && (
                  <p className="text-gray-600 text-sm">
                    Already have an account?{' '}
                    <button
                      onClick={() => setAuthState(prev => ({ ...prev, mode: 'login' }))}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Sign in
                    </button>
                  </p>
                )}

                {authState.mode === 'forgot-password' && (
                  <p className="text-gray-600 text-sm">
                    Remember your password?{' '}
                    <button
                      onClick={() => setAuthState(prev => ({ ...prev, mode: 'login' }))}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Sign in
                    </button>
                  </p>
                )}
              </div>
            </motion.div>
          )}

          {/* Onboarding Flow */}
          {authState.mode === 'onboarding' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-2xl shadow-xl p-8"
            >
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-2xl mb-4">
                  <CheckCircleIcon className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  Welcome to ReliQuary!
                </h2>
                <p className="text-gray-600">
                  Let's complete your setup and get you started
                </p>
              </div>

              {/* Success Message */}
              {authState.success && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center"
                >
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mr-3" />
                  <span className="text-green-700 text-sm">{authState.success}</span>
                </motion.div>
              )}

              {/* Error Message */}
              {authState.error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center"
                >
                  <ExclamationCircleIcon className="h-5 w-5 text-red-600 mr-3" />
                  <span className="text-red-700 text-sm">{authState.error}</span>
                </motion.div>
              )}

              {/* Additional Onboarding Fields */}
              <div className="space-y-6 mb-8">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organization Type
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => handleInputChange('role', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  >
                    <option value="">Select organization type</option>
                    {ORGANIZATION_TYPES.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Role
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => handleInputChange('role', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  >
                    <option value="">Select your role</option>
                    {USER_ROLES.map((role) => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Next Steps */}
              <div className="bg-blue-50 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">What's Next?</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                    Generate your first API key
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                    Explore our documentation
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                    Set up your first vault
                  </li>
                </ul>
              </div>

              <button
                onClick={handleCompleteOnboarding}
                disabled={authState.loading}
                className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {authState.loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Setting up your account...
                  </div>
                ) : (
                  <>
                    Go to Dashboard
                    <ArrowRightIcon className="h-5 w-5 ml-2" />
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}