'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  RocketLaunchIcon,
  PhoneIcon,
  DocumentTextIcon,
  PlayIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const ctaOptions = [
  {
    icon: RocketLaunchIcon,
    title: 'Start Free Trial',
    description: 'Get started immediately with our Developer plan',
    benefits: ['No credit card required', '1,000 free API calls', 'Full platform access'],
    cta: 'Try Free Now',
    href: '/signup',
    color: 'primary'
  },
  {
    icon: PhoneIcon,
    title: 'Talk to Sales',
    description: 'Discuss enterprise needs with our security experts',
    benefits: ['Custom pricing', 'Architecture review', 'Implementation support'],
    cta: 'Schedule Call',
    href: '/contact',
    color: 'secondary'
  },
  {
    icon: DocumentTextIcon,
    title: 'View Documentation',
    description: 'Explore our comprehensive API and integration guides',
    benefits: ['Complete API reference', 'Code examples', 'Best practices'],
    cta: 'Read Docs',
    href: '/docs',
    color: 'tertiary'
  }
];

const quickActions = [
  { label: 'API Reference', href: '/api-reference', icon: DocumentTextIcon },
  { label: 'Live Demo', href: '/demo', icon: PlayIcon },
  { label: 'Security Whitepaper', href: '/security-whitepaper', icon: CheckCircleIcon },
  { label: 'Implementation Guide', href: '/implementation', icon: ArrowRightIcon }
];

export default function CTA() {
  return (
    <section className="section-padding bg-gradient-to-br from-primary-600 via-primary-700 to-purple-800 text-white relative overflow-hidden">
      
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-600/20 to-purple-600/20"></div>
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/4 right-1/4 w-64 h-64 bg-white/5 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -50, 0],
            y: [0, 100, 0],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-1/4 left-1/4 w-48 h-48 bg-purple-300/10 rounded-full blur-2xl"
        />
      </div>

      <div className="container-custom relative z-10">
        
        {/* Main CTA Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto mb-16"
        >
          <h2 className="heading-lg mb-6">
            Ready to Secure Your Future?
          </h2>
          <p className="text-xl lg:text-2xl text-primary-100 mb-8">
            Join thousands of developers and enterprises who trust ReliQuary 
            to protect their most sensitive data with quantum-safe security.
          </p>
          
          {/* Primary CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              href="/signup"
              className="inline-flex items-center justify-center bg-white text-primary-700 font-semibold py-4 px-8 rounded-lg hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              <RocketLaunchIcon className="h-5 w-5 mr-2" />
              Start Free Trial
            </Link>
            <Link
              href="/demo"
              className="inline-flex items-center justify-center border-2 border-white text-white font-semibold py-4 px-8 rounded-lg hover:bg-white hover:text-primary-700 transition-all duration-300"
            >
              <PlayIcon className="h-5 w-5 mr-2" />
              Watch Demo
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-8 text-primary-200">
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5" />
              <span>14-day free trial</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </motion.div>

        {/* CTA Options Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid md:grid-cols-3 gap-8 mb-16"
        >
          {ctaOptions.map((option, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300 group"
            >
              <div className={`inline-flex p-3 rounded-lg mb-4 ${
                option.color === 'primary' ? 'bg-white/20' :
                option.color === 'secondary' ? 'bg-purple-500/30' :
                'bg-blue-500/30'
              }`}>
                <option.icon className="h-8 w-8" />
              </div>
              
              <h3 className="text-xl font-semibold mb-3">{option.title}</h3>
              <p className="text-primary-100 mb-6">{option.description}</p>
              
              <ul className="space-y-2 mb-6">
                {option.benefits.map((benefit, benefitIndex) => (
                  <li key={benefitIndex} className="flex items-center space-x-2">
                    <CheckCircleIcon className="h-4 w-4 text-green-300" />
                    <span className="text-sm text-primary-100">{benefit}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={option.href}
                className="inline-flex items-center justify-center w-full bg-white/20 text-white font-semibold py-3 px-6 rounded-lg hover:bg-white/30 transition-all duration-300 group-hover:transform group-hover:scale-105"
              >
                {option.cta}
                <ArrowRightIcon className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          ))}
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center"
        >
          <h3 className="text-xl font-semibold mb-6 text-primary-100">
            Or explore these resources
          </h3>
          
          <div className="flex flex-wrap justify-center gap-4">
            {quickActions.map((action, index) => (
              <Link
                key={index}
                href={action.href}
                className="inline-flex items-center space-x-2 bg-white/10 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-300 text-sm"
              >
                <action.icon className="h-4 w-4" />
                <span>{action.label}</span>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Final Trust Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center mt-16 pt-16 border-t border-white/20"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="text-2xl font-bold">99.99%</div>
              <div className="text-primary-200 text-sm">Uptime SLA</div>
            </div>
            <div>
              <div className="text-2xl font-bold">SOC 2</div>
              <div className="text-primary-200 text-sm">Compliant</div>
            </div>
            <div>
              <div className="text-2xl font-bold">24/7</div>
              <div className="text-primary-200 text-sm">Support</div>
            </div>
            <div>
              <div className="text-2xl font-bold">256-bit</div>
              <div className="text-primary-200 text-sm">Quantum Safe</div>
            </div>
          </div>
          
          <p className="text-primary-100 text-sm">
            Trusted by Fortune 500 companies and startups alike. 
            <Link href="/security" className="underline hover:text-white transition-colors">
              Learn about our security measures
            </Link>
          </p>
        </motion.div>
      </div>
    </section>
  );
}