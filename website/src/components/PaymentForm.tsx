// Payment Form Component
// Handles Stripe payment processing with card elements and India-specific payment methods

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CreditCardIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  BanknotesIcon,
  QrCodeIcon
} from '@heroicons/react/24/outline';
import { useBilling } from '@/contexts/BillingContext';
import { stripeService } from '@/lib/stripe';

interface PaymentFormProps {
  planId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export default function PaymentForm({ planId, onSuccess, onCancel }: PaymentFormProps) {
  const { customer, plans, loading: billingLoading } = useBilling();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'upi' | 'netbanking'>('card');
  const [cardholderName, setCardholderName] = useState('');
  const [cardNumber, setCardNumber] = useState('');
  const [expiry, setExpiry] = useState('');
  const [cvc, setCvc] = useState('');
  const [upiId, setUpiId] = useState('');
  const [saveCard, setSaveCard] = useState(true);

  const selectedPlan = plans.find(plan => plan.id === planId);

  // Format card number input
  const formatCardNumber = (value: string) => {
    const cleaned = value.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{0,4})(\d{0,4})(\d{0,4})(\d{0,4})$/);
    if (match) {
      return match.slice(1).filter(Boolean).join(' ');
    }
    return cleaned;
  };

  // Format expiry input
  const formatExpiry = (value: string) => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length >= 3) {
      return `${cleaned.slice(0, 2)}/${cleaned.slice(2, 4)}`;
    }
    return cleaned;
  };

  // Handle card number input
  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCardNumber(e.target.value);
    setCardNumber(formatted);
  };

  // Handle expiry input
  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatExpiry(e.target.value);
    setExpiry(formatted);
  };

  // Validate form
  const validateForm = () => {
    if (paymentMethod === 'card') {
      if (!cardholderName.trim()) {
        setError('Please enter the cardholder name');
        return false;
      }

      const cleanedCardNumber = cardNumber.replace(/\s/g, '');
      if (cleanedCardNumber.length < 16) {
        setError('Please enter a valid card number');
        return false;
      }

      const [month, year] = expiry.split('/');
      if (!month || !year || month.length !== 2 || year.length !== 2) {
        setError('Please enter a valid expiration date');
        return false;
      }

      const monthNum = parseInt(month, 10);
      const yearNum = parseInt(year, 10);
      const currentYear = new Date().getFullYear() % 100;
      const currentMonth = new Date().getMonth() + 1;

      if (yearNum < currentYear || (yearNum === currentYear && monthNum < currentMonth)) {
        setError('Card has expired');
        return false;
      }

      if (cvc.length < 3) {
        setError('Please enter a valid CVC');
        return false;
      }
    } else if (paymentMethod === 'upi') {
      if (!upiId.trim()) {
        setError('Please enter your UPI ID');
        return false;
      }
      
      // Basic UPI validation
      if (!upiId.includes('@')) {
        setError('Please enter a valid UPI ID (e.g., username@bank)');
        return false;
      }
    }

    return true;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    if (!customer || !selectedPlan) return;

    setLoading(true);
    setError(null);

    try {
      // In a real implementation, you would:
      // 1. Create a payment method with Stripe.js
      // 2. Create a payment intent or subscription
      // 3. Confirm the payment with Stripe.js

      // For demo purposes, we'll simulate the payment process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate successful payment
      setSuccess(true);
      
      // Call onSuccess callback after a short delay
      setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (err) {
      console.error('Payment failed:', err);
      setError('Payment failed. Please check your payment details and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Reset form when plan changes
  useEffect(() => {
    setSuccess(false);
    setError(null);
  }, [planId]);

  if (billingLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!selectedPlan) {
    return (
      <div className="text-center p-8">
        <ExclamationCircleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Plan Not Found</h3>
        <p className="text-gray-600">The selected plan could not be found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AnimatePresence mode="wait">
        {!success ? (
          <motion.div
            key="payment-form"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Plan Summary */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">{selectedPlan.name} Plan</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    ${selectedPlan.price}/{selectedPlan.interval}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900 dark:text-white">
                    ${selectedPlan.price}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    per {selectedPlan.interval}
                  </p>
                </div>
              </div>
            </div>

            {/* Payment Method Selection - India Specific */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Payment Method</h3>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setPaymentMethod('card')}
                  className={`p-3 rounded-lg border text-center transition-colors ${
                    paymentMethod === 'card'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <CreditCardIcon className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-xs">Card</span>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPaymentMethod('upi')}
                  className={`p-3 rounded-lg border text-center transition-colors ${
                    paymentMethod === 'upi'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <QrCodeIcon className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-xs">UPI</span>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPaymentMethod('netbanking')}
                  className={`p-3 rounded-lg border text-center transition-colors ${
                    paymentMethod === 'netbanking'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <BanknotesIcon className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-xs">Net Banking</span>
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center"
              >
                <ExclamationCircleIcon className="h-5 w-5 text-red-600 dark:text-red-400 mr-3" />
                <span className="text-red-700 dark:text-red-300 text-sm">{error}</span>
              </motion.div>
            )}

            {/* Payment Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {paymentMethod === 'card' && (
                <>
                  {/* Cardholder Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Cardholder Name
                    </label>
                    <input
                      type="text"
                      value={cardholderName}
                      onChange={(e) => setCardholderName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="John Doe"
                      required
                    />
                  </div>

                  {/* Card Number */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Card Number
                    </label>
                    <div className="relative">
                      <CreditCardIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        value={cardNumber}
                        onChange={handleCardNumberChange}
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="1234 5678 9012 3456"
                        maxLength={19}
                        required
                      />
                    </div>
                  </div>

                  {/* Expiry and CVC */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Expiration Date
                      </label>
                      <input
                        type="text"
                        value={expiry}
                        onChange={handleExpiryChange}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="MM/YY"
                        maxLength={5}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        CVC
                      </label>
                      <input
                        type="text"
                        value={cvc}
                        onChange={(e) => setCvc(e.target.value.replace(/\D/g, ''))}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="123"
                        maxLength={4}
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {paymentMethod === 'upi' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    UPI ID
                  </label>
                  <input
                    type="text"
                    value={upiId}
                    onChange={(e) => setUpiId(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="username@bank"
                    required
                  />
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    You'll be redirected to your UPI app to complete the payment
                  </p>
                </div>
              )}

              {paymentMethod === 'netbanking' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Bank
                  </label>
                  <select className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                    <option>Select your bank</option>
                    <option>State Bank of India</option>
                    <option>HDFC Bank</option>
                    <option>ICICI Bank</option>
                    <option>Axis Bank</option>
                    <option>Kotak Mahindra Bank</option>
                    <option>Bank of Baroda</option>
                    <option>Punjab National Bank</option>
                  </select>
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    You'll be redirected to your bank's website to complete the payment
                  </p>
                </div>
              )}

              {/* Save Card */}
              {paymentMethod === 'card' && (
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="save-card"
                    checked={saveCard}
                    onChange={(e) => setSaveCard(e.target.checked)}
                    className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 bg-white dark:bg-gray-800"
                  />
                  <label htmlFor="save-card" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Save card for future payments
                  </label>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={onCancel}
                  className="flex-1 px-4 py-3 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    `Pay $${selectedPlan.price}`
                  )}
                </button>
              </div>
            </form>
            
            <div className="text-center text-sm text-gray-500 dark:text-gray-400 pt-4">
              <p>Secure payment processing powered by Stripe</p>
              <p className="mt-1">All transactions are encrypted and secure</p>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-8"
          >
            <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Payment Successful!</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Your subscription to the {selectedPlan.name} plan has been activated.
            </p>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 inline-block">
              <p className="text-sm text-gray-600 dark:text-gray-400">Redirecting to your dashboard...</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}