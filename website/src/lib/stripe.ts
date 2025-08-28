// Mock Stripe service for demonstration purposes
// In a real implementation, this would integrate with the actual Stripe API

export interface Customer {
  id: string;
  email: string;
  name: string;
  subscription?: Subscription;
  paymentMethods: PaymentMethod[];
}

export interface Subscription {
  id: string;
  plan: SubscriptionPlan;
  status: 'active' | 'inactive' | 'canceled';
  currentPeriodEnd: number;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  interval: 'month' | 'year';
  features: string[];
  limitations: string[];
  popular?: boolean;
}

export interface PaymentMethod {
  id: string;
  type: 'card';
  card: {
    brand: string;
    last4: string;
    expMonth: number;
    expYear: number;
  };
  isDefault: boolean;
}

export interface Invoice {
  id: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  created: number;
  periodStart: number;
  periodEnd: number;
}

class StripeService {
  private initialized = false;

  async initialize() {
    // Simulate initialization
    await new Promise(resolve => setTimeout(resolve, 500));
    this.initialized = true;
    return true;
  }

  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    return [
      {
        id: 'free',
        name: 'Developer',
        description: 'Perfect for developers and small projects',
        price: 0,
        interval: 'month',
        features: [
          '1,000 API calls/month',
          'Basic cryptographic operations',
          'Standard algorithms (AES, RSA)',
          'Community support',
          'Self-hosting allowed',
          '99% uptime SLA',
          'Basic documentation',
          'GitHub integration'
        ],
        limitations: [
          'No advanced features',
          'No priority support',
          'No enterprise integrations'
        ]
      },
      {
        id: 'starter',
        name: 'Starter',
        description: 'For growing teams and production workloads',
        price: 99,
        interval: 'month',
        features: [
          '10,000 API calls/month',
          'All cryptographic features',
          'Post-quantum algorithms',
          'Multi-agent consensus',
          'Email support',
          'Basic analytics',
          '99.9% uptime SLA',
          'Slack integration',
          'REST API access',
          'Standard rate limits'
        ],
        limitations: [
          'No zero-knowledge proofs',
          'No custom deployment',
          'No dedicated support'
        ]
      },
      {
        id: 'professional',
        name: 'Professional',
        description: 'For professional teams and growing businesses',
        price: 499,
        interval: 'month',
        features: [
          '100,000 API calls/month',
          'Advanced features (ZK proofs)',
          'Threshold cryptography',
          'SSO integration',
          'Priority email support',
          'Advanced analytics',
          'Custom dashboards',
          '99.9% uptime SLA',
          'Webhook support',
          'Team collaboration',
          'Audit logging',
          'Compliance reports'
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
        description: 'For large organizations with advanced needs',
        price: 1999,
        interval: 'month',
        features: [
          'Unlimited API calls',
          'All features included',
          'Custom deployment options',
          'Dedicated support manager',
          'Professional services',
          'Custom SLA (up to 99.99%)',
          'On-premise deployment',
          'White-label options',
          'Priority feature requests',
          'Training & onboarding',
          'Advanced security',
          '24/7 phone support'
        ],
        limitations: []
      }
    ];
  }

  async getCustomer(customerId: string): Promise<Customer> {
    // Mock customer data
    return {
      id: customerId,
      email: 'user@example.com',
      name: 'Demo User',
      subscription: {
        id: 'sub_123456789',
        plan: (await this.getSubscriptionPlans())[0],
        status: 'active',
        currentPeriodEnd: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60
      },
      paymentMethods: []
    };
  }

  async getPaymentMethods(customerId: string): Promise<PaymentMethod[]> {
    return [];
  }

  async getInvoices(customerId: string): Promise<Invoice[]> {
    return [];
  }

  async createSubscription(customerId: string, planId: string): Promise<Subscription> {
    const plans = await this.getSubscriptionPlans();
    const plan = plans.find(p => p.id === planId);
    
    if (!plan) {
      throw new Error('Plan not found');
    }

    return {
      id: 'sub_' + Math.random().toString(36).substr(2, 9),
      plan,
      status: 'active',
      currentPeriodEnd: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60
    };
  }

  async updateSubscription(subscriptionId: string, planId: string): Promise<void> {
    // Mock implementation
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  async cancelSubscription(subscriptionId: string): Promise<void> {
    // Mock implementation
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  async addPaymentMethod(customerId: string, paymentMethodId: string): Promise<PaymentMethod> {
    // Mock implementation
    return {
      id: 'pm_' + Math.random().toString(36).substr(2, 9),
      type: 'card',
      card: {
        brand: 'visa',
        last4: '4242',
        expMonth: 12,
        expYear: 2025
      },
      isDefault: true
    };
  }

  // India-specific payment methods
  getSupportedPaymentMethodsForIndia() {
    return [
      'card', // Credit/Debit cards
      'upi',  // Unified Payments Interface
      'netbanking', // Internet banking
      'wallet', // Digital wallets
      'emandate' // Electronic mandates for recurring payments
    ];
  }

  // Check if a payment method is supported in India
  isPaymentMethodSupportedInIndia(method: string) {
    return this.getSupportedPaymentMethodsForIndia().includes(method);
  }
}

export const stripeService = new StripeService();