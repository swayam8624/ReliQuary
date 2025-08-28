'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  CheckIcon, 
  XMarkIcon,
  SparklesIcon,
  BuildingOfficeIcon,
  CpuChipIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const pricingTiers = [
  {
    name: 'Developer',
    icon: CpuChipIcon,
    price: { monthly: 0, yearly: 0 },
    description: 'Perfect for developers and small projects',
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
    ],
    cta: 'Start Free',
    href: '/signup?plan=developer',
    popular: false,
    color: 'gray'
  },
  {
    name: 'Starter',
    icon: SparklesIcon,
    price: { monthly: 99, yearly: 990 },
    description: 'For growing teams and production workloads',
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
    ],
    cta: 'Start Trial',
    href: '/signup?plan=starter',
    popular: false,
    color: 'blue'
  },
  {
    name: 'Professional',
    icon: BuildingOfficeIcon,
    price: { monthly: 499, yearly: 4990 },
    description: 'For professional teams and growing businesses',
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
    cta: 'Start Trial',
    href: '/signup?plan=professional',
    popular: true,
    color: 'primary'
  },
  {
    name: 'Enterprise',
    icon: ShieldCheckIcon,
    price: { monthly: 1999, yearly: 19990 },
    description: 'For large organizations with advanced needs',
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
    limitations: [],
    cta: 'Contact Sales',
    href: '/contact?plan=enterprise',
    popular: false,
    color: 'purple'
  }
];

const enterprisePlusFeatures = [
  'Source code access',
  'Custom development',
  'Dedicated infrastructure',
  'Regulatory compliance',
  'Global deployment',
  'Custom integrations'
];

const faqs = [
  {
    question: 'What happens when I exceed my plan limits?',
    answer: 'We\'ll notify you when you approach your limits. You can upgrade your plan or purchase additional capacity. We never cut off service without warning.'
  },
  {
    question: 'Can I change plans anytime?',
    answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we\'ll prorate any billing adjustments.'
  },
  {
    question: 'Do you offer custom enterprise pricing?',
    answer: 'Yes, we work with large organizations to create custom pricing based on volume, specific requirements, and deployment needs.'
  },
  {
    question: 'Is there a free trial for paid plans?',
    answer: 'Yes, all paid plans include a 14-day free trial with full access to features. No credit card required to start.'
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards, ACH transfers, and can arrange invoicing for enterprise customers.'
  }
];

export default function Pricing() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const getSavings = (monthly: number, yearly: number) => {
    if (monthly === 0) return 0;
    return Math.round(((monthly * 12 - yearly) / (monthly * 12)) * 100);
  };

  return (
    <section id="pricing" className="section-padding bg-gradient-to-b from-white to-gray-50">
      <div className="container-custom">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <h2 className="heading-lg text-gray-900 mb-6">
            Simple, Transparent Pricing
          </h2>
          <p className="text-large text-gray-600 mb-8">
            Choose the perfect plan for your needs. Start free and scale as you grow.
            All plans include our core security features.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center p-1 bg-gray-100 rounded-lg">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                billingCycle === 'yearly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Yearly
              <span className="ml-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {pricingTiers.map((tier, index) => {
            const price = tier.price[billingCycle];
            const savings = getSavings(tier.price.monthly, tier.price.yearly);
            
            return (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`pricing-card ${tier.popular ? 'featured' : ''}`}
              >
                <div className="flex items-center space-x-3 mb-4">
                  <tier.icon className={`h-8 w-8 ${
                    tier.color === 'primary' ? 'text-primary-600' :
                    tier.color === 'purple' ? 'text-purple-600' :
                    tier.color === 'blue' ? 'text-blue-600' :
                    'text-gray-600'
                  }`} />
                  <h3 className="text-xl font-bold text-gray-900">{tier.name}</h3>
                </div>

                <p className="text-gray-600 mb-6">{tier.description}</p>

                <div className="mb-6">
                  <div className="flex items-baseline">
                    <span className="text-4xl font-bold text-gray-900">
                      ${price === 0 ? '0' : price.toLocaleString()}
                    </span>
                    {price > 0 && (
                      <span className="text-gray-600 ml-2">
                        /{billingCycle === 'monthly' ? 'month' : 'year'}
                      </span>
                    )}
                  </div>
                  {billingCycle === 'yearly' && savings > 0 && (
                    <div className="text-sm text-green-600 font-medium">
                      Save {savings}% with annual billing
                    </div>
                  )}
                </div>

                <Link
                  href={tier.href}
                  className={`block w-full text-center py-3 px-6 rounded-lg font-semibold transition-all duration-300 mb-6 ${
                    tier.popular
                      ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-lg hover:shadow-xl'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {tier.cta}
                </Link>

                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Features included:</h4>
                  <ul className="space-y-2">
                    {tier.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start space-x-3">
                        <CheckIcon className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {tier.limitations.length > 0 && (
                    <div className="pt-4 border-t border-gray-100">
                      <h5 className="text-sm font-medium text-gray-500 mb-2">Not included:</h5>
                      <ul className="space-y-1">
                        {tier.limitations.map((limitation, limitIndex) => (
                          <li key={limitIndex} className="flex items-start space-x-3">
                            <XMarkIcon className="h-4 w-4 text-gray-400 flex-shrink-0 mt-0.5" />
                            <span className="text-xs text-gray-500">{limitation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Enterprise Plus */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-8 text-white mb-16"
        >
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold mb-4">Enterprise+</h3>
              <p className="text-purple-100 mb-6">
                For organizations requiring the highest level of customization, security, and support.
                Starting at $9,999/month with custom pricing based on your specific needs.
              </p>
              <div className="grid grid-cols-2 gap-4 mb-6">
                {enterprisePlusFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-300" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="text-center lg:text-right">
              <div className="text-3xl font-bold mb-2">Custom Pricing</div>
              <div className="text-purple-200 mb-6">Starting at $9,999/month</div>
              <Link
                href="/contact?plan=enterprise-plus"
                className="inline-block bg-white text-purple-600 font-semibold py-3 px-6 rounded-lg hover:bg-gray-100 transition-colors"
              >
                Schedule Consultation
              </Link>
            </div>
          </div>
        </motion.div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl mx-auto"
        >
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Frequently Asked Questions
          </h3>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full text-left p-6 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-gray-900">{faq.question}</h4>
                    <motion.div
                      animate={{ rotate: openFaq === index ? 180 : 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                    </motion.div>
                  </div>
                </button>
                <motion.div
                  initial={false}
                  animate={{
                    height: openFaq === index ? 'auto' : 0,
                    opacity: openFaq === index ? 1 : 0
                  }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="px-6 pb-6">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                </motion.div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mt-16"
        >
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Get Started?
          </h3>
          <p className="text-gray-600 mb-6">
            Join thousands of developers and enterprises securing their applications with ReliQuary.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="btn-primary">
              Start Free Trial
            </Link>
            <Link href="/contact" className="btn-outline">
              Talk to Sales
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}