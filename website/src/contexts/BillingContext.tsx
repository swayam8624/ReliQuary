// Billing Context
// Manages billing state and operations across the application

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { stripeService, type Customer, type SubscriptionPlan, type PaymentMethod, type Invoice } from '@/lib/stripe';

interface BillingContextType {
  customer: Customer | null;
  plans: SubscriptionPlan[];
  paymentMethods: PaymentMethod[];
  invoices: Invoice[];
  loading: boolean;
  error: string | null;
  selectedPlan: SubscriptionPlan | null;
  initializeBilling: () => Promise<void>;
  selectPlan: (planId: string) => void;
  subscribeToPlan: (planId: string, paymentMethod?: string) => Promise<{ success: boolean; error?: string }>;
  updateSubscription: (planId: string) => Promise<{ success: boolean; error?: string }>;
  cancelSubscription: () => Promise<{ success: boolean; error?: string }>;
  addPaymentMethod: (paymentMethodId: string) => Promise<{ success: boolean; error?: string }>;
  setDefaultPaymentMethod: (paymentMethodId: string) => Promise<{ success: boolean; error?: string }>;
  removePaymentMethod: (paymentMethodId: string) => Promise<{ success: boolean; error?: string }>;
  refreshCustomer: () => Promise<void>;
  refreshInvoices: () => Promise<void>;
  // India-specific methods
  getSupportedPaymentMethodsForRegion: (region: string) => string[];
}

const BillingContext = createContext<BillingContextType | undefined>(undefined);

export function BillingProvider({ children }: { children: ReactNode }) {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);

  // Initialize billing
  const initializeBilling = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Initialize Stripe
      await stripeService.initialize();
      
      // Fetch plans
      const fetchedPlans = await stripeService.getSubscriptionPlans();
      setPlans(fetchedPlans);
      
      // Fetch customer data
      // In a real implementation, you would get the customer ID from auth context
      const customerId = 'cus_123456789'; // Mock customer ID
      const customerData = await stripeService.getCustomer(customerId);
      setCustomer(customerData);
      
      // Set initial selected plan
      if (customerData.subscription) {
        setSelectedPlan(customerData.subscription.plan);
      } else {
        // Default to free plan if no subscription
        const freePlan = fetchedPlans.find(plan => plan.id === 'free');
        if (freePlan) setSelectedPlan(freePlan);
      }
      
      // Fetch payment methods
      const methods = await stripeService.getPaymentMethods(customerId);
      setPaymentMethods(methods);
      
      // Fetch invoices
      const customerInvoices = await stripeService.getInvoices(customerId);
      setInvoices(customerInvoices);
    } catch (err) {
      console.error('Failed to initialize billing:', err);
      setError('Failed to load billing information. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Select a plan
  const selectPlan = (planId: string) => {
    const plan = plans.find(p => p.id === planId);
    if (plan) {
      setSelectedPlan(plan);
    }
  };

  // Subscribe to a plan
  const subscribeToPlan = async (planId: string, paymentMethod?: string) => {
    if (!customer) {
      return { success: false, error: 'Customer not found' };
    }

    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would involve:
      // 1. Creating a subscription in Stripe
      // 2. Handling the payment flow with Stripe Elements
      // 3. Updating the customer's subscription status
      
      // For India-specific payment methods:
      if (paymentMethod && paymentMethod !== 'card') {
        // Handle UPI, Net Banking, etc.
        // This would redirect to the appropriate payment gateway
        console.log(`Processing ${paymentMethod} payment for India`);
      }
      
      await stripeService.createSubscription(customer.id, planId);
      
      // Refresh customer data
      await refreshCustomer();
      
      return { success: true };
    } catch (err) {
      console.error('Failed to subscribe to plan:', err);
      return { success: false, error: 'Failed to subscribe to plan. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Update subscription
  const updateSubscription = async (planId: string) => {
    if (!customer?.subscription) {
      return { success: false, error: 'No active subscription found' };
    }

    try {
      setLoading(true);
      setError(null);
      
      // Update subscription in Stripe
      await stripeService.updateSubscription(customer.subscription.id, planId);
      
      // Refresh customer data
      await refreshCustomer();
      
      return { success: true };
    } catch (err) {
      console.error('Failed to update subscription:', err);
      return { success: false, error: 'Failed to update subscription. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Cancel subscription
  const cancelSubscription = async () => {
    if (!customer?.subscription) {
      return { success: false, error: 'No active subscription found' };
    }

    try {
      setLoading(true);
      setError(null);
      
      // Cancel subscription in Stripe
      await stripeService.cancelSubscription(customer.subscription.id);
      
      // Refresh customer data
      await refreshCustomer();
      
      return { success: true };
    } catch (err) {
      console.error('Failed to cancel subscription:', err);
      return { success: false, error: 'Failed to cancel subscription. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Add payment method
  const addPaymentMethod = async (paymentMethodId: string) => {
    if (!customer) {
      return { success: false, error: 'Customer not found' };
    }

    try {
      setLoading(true);
      setError(null);
      
      // Add payment method in Stripe
      const newMethod = await stripeService.addPaymentMethod(customer.id, paymentMethodId);
      
      // Update payment methods list
      setPaymentMethods(prev => [...prev, newMethod]);
      
      return { success: true };
    } catch (err) {
      console.error('Failed to add payment method:', err);
      return { success: false, error: 'Failed to add payment method. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Set default payment method
  const setDefaultPaymentMethod = async (paymentMethodId: string) => {
    if (!customer) {
      return { success: false, error: 'Customer not found' };
    }

    try {
      setLoading(true);
      setError(null);
      
      // Update in Stripe
      await stripeService.addPaymentMethod(customer.id, paymentMethodId);
      
      // Refresh payment methods
      const methods = await stripeService.getPaymentMethods(customer.id);
      setPaymentMethods(methods);
      
      return { success: true };
    } catch (err) {
      console.error('Failed to set default payment method:', err);
      return { success: false, error: 'Failed to set default payment method. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Remove payment method
  const removePaymentMethod = async (paymentMethodId: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // Remove from state (in a real implementation, you would call Stripe API)
      setPaymentMethods(prev => prev.filter(method => method.id !== paymentMethodId));
      
      return { success: true };
    } catch (err) {
      console.error('Failed to remove payment method:', err);
      return { success: false, error: 'Failed to remove payment method. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Refresh customer data
  const refreshCustomer = async () => {
    if (!customer) return;
    
    try {
      const updatedCustomer = await stripeService.getCustomer(customer.id);
      setCustomer(updatedCustomer);
    } catch (err) {
      console.error('Failed to refresh customer data:', err);
    }
  };

  // Refresh invoices
  const refreshInvoices = async () => {
    if (!customer) return;
    
    try {
      const customerInvoices = await stripeService.getInvoices(customer.id);
      setInvoices(customerInvoices);
    } catch (err) {
      console.error('Failed to refresh invoices:', err);
    }
  };

  // Get supported payment methods for a region
  const getSupportedPaymentMethodsForRegion = (region: string) => {
    if (region.toLowerCase() === 'india') {
      return stripeService.getSupportedPaymentMethodsForIndia();
    }
    // Default to standard payment methods
    return ['card'];
  };

  const value = {
    customer,
    plans,
    paymentMethods,
    invoices,
    loading,
    error,
    selectedPlan,
    initializeBilling,
    selectPlan,
    subscribeToPlan,
    updateSubscription,
    cancelSubscription,
    addPaymentMethod,
    setDefaultPaymentMethod,
    removePaymentMethod,
    refreshCustomer,
    refreshInvoices,
    getSupportedPaymentMethodsForRegion
  };

  return (
    <BillingContext.Provider value={value}>
      {children}
    </BillingContext.Provider>
  );
}

export function useBilling() {
  const context = useContext(BillingContext);
  if (context === undefined) {
    throw new Error('useBilling must be used within a BillingProvider');
  }
  return context;
}