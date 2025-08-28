'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  ShieldCheckIcon, 
  LightBulbIcon, 
  CloudArrowUpIcon,
  PlayIcon,
  ChartBarIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

const features = [
  {
    icon: ShieldCheckIcon,
    title: 'Post-Quantum Secure',
    description: 'Advanced quantum-resistant cryptography'
  },
  {
    icon: CpuChipIcon,
    title: 'Multi-Agent Consensus',
    description: 'Distributed decision-making intelligence'
  },
  {
    icon: LightBulbIcon,
    title: 'Zero-Knowledge Proofs',
    description: 'Privacy-preserving verification'
  },
  {
    icon: CloudArrowUpIcon,
    title: 'Enterprise Ready',
    description: 'Production-grade scalability'
  }
];

const stats = [
  { value: '99.99%', label: 'Uptime SLA' },
  { value: '< 200ms', label: 'Response Time' },
  { value: '256-bit', label: 'Encryption' },
  { value: '100+', label: 'Enterprise Clients' }
];

const codeExample = `# Install ReliQuary SDK
pip install reliquary-sdk

# Initialize secure vault
from reliquary import SecureVault

vault = SecureVault()
result = vault.store_secret(
    data="sensitive_data",
    context_required=True,
    consensus_threshold=3
)

print(f"Stored with ID: {result.vault_id}")`;

export default function Hero() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [currentFeature, setCurrentFeature] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center hero-bg overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50"></div>
      
      {/* Animated Background Shapes */}
      <div className="absolute inset-0">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/4 left-1/4 w-32 h-32 bg-primary-200 rounded-full opacity-20 blur-xl"
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
          className="absolute top-3/4 right-1/4 w-48 h-48 bg-accent-200 rounded-full opacity-20 blur-xl"
        />
      </div>

      <div className="container-custom relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          
          {/* Content */}
          <div className="text-center lg:text-left">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-6"
            >
              {/* Badge */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="inline-flex items-center px-4 py-2 rounded-full bg-primary-50 border border-primary-200 text-primary-700 text-sm font-medium"
              >
                <ShieldCheckIcon className="h-4 w-4 mr-2" />
                Now Available - Production Ready v5.0
              </motion.div>

              {/* Main Headline */}
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="heading-xl gradient-text"
              >
                Enterprise-Grade
                <br />
                <span className="text-primary-600">Cryptographic Memory</span>
                <br />
                Platform
              </motion.h1>

              {/* Subtitle */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="text-large text-gray-600 max-w-2xl mx-auto lg:mx-0"
              >
                Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, 
                multi-agent consensus, and zero-knowledge proofs. Built for the quantum computing era.
              </motion.p>

              {/* CTA Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
              >
                <Link href="/signup" className="btn-primary">
                  Start Free Trial
                </Link>
                <button
                  onClick={() => setIsVideoPlaying(true)}
                  className="btn-outline flex items-center justify-center space-x-2"
                >
                  <PlayIcon className="h-5 w-5" />
                  <span>Watch Demo</span>
                </button>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-8"
              >
                {stats.map((stat, index) => (
                  <div key={index} className="text-center lg:text-left">
                    <div className="text-2xl font-bold text-primary-600">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                  </div>
                ))}
              </motion.div>
            </motion.div>
          </div>

          {/* Right Column - Interactive Demo */}
          <div className="relative">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="space-y-8"
            >
              {/* Code Example */}
              <div className="relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg blur opacity-25"></div>
                <div className="relative bg-gray-900 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center space-x-2 mb-4">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-gray-400 text-sm ml-4">reliquary-demo.py</span>
                  </div>
                  <pre className="text-green-400 text-sm overflow-x-auto">
                    <code>{codeExample}</code>
                  </pre>
                </div>
              </div>

              {/* Feature Showcase */}
              <div className="grid grid-cols-2 gap-4">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ 
                      opacity: currentFeature === index ? 1 : 0.7,
                      scale: currentFeature === index ? 1 : 0.95
                    }}
                    transition={{ duration: 0.3 }}
                    className={`card ${
                      currentFeature === index 
                        ? 'border-primary-200 bg-primary-50' 
                        : 'border-gray-200'
                    }`}
                  >
                    <feature.icon className={`h-8 w-8 mb-3 ${
                      currentFeature === index ? 'text-primary-600' : 'text-gray-600'
                    }`} />
                    <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </motion.div>
                ))}
              </div>

              {/* Trust Indicators */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="flex items-center justify-center lg:justify-start space-x-6 text-sm text-gray-500"
              >
                <div className="flex items-center space-x-2">
                  <ShieldCheckIcon className="h-5 w-5 text-green-500" />
                  <span>SOC 2 Compliant</span>
                </div>
                <div className="flex items-center space-x-2">
                  <ShieldCheckIcon className="h-5 w-5 text-green-500" />
                  <span>GDPR Ready</span>
                </div>
                <div className="flex items-center space-x-2">
                  <ChartBarIcon className="h-5 w-5 text-green-500" />
                  <span>99.99% SLA</span>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Video Modal */}
      {isVideoPlaying && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
          onClick={() => setIsVideoPlaying(false)}
        >
          <div className="relative max-w-4xl w-full mx-4">
            <button
              onClick={() => setIsVideoPlaying(false)}
              className="absolute -top-12 right-0 text-white hover:text-gray-300"
            >
              <XMarkIcon className="h-8 w-8" />
            </button>
            <div className="aspect-video bg-gray-900 rounded-lg flex items-center justify-center">
              <div className="text-white text-center">
                <PlayIcon className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">Demo Video Coming Soon</p>
                <p className="text-sm text-gray-400 mt-2">
                  Interactive platform walkthrough and features showcase
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center"
        >
          <div className="w-1 h-3 bg-gray-400 rounded-full mt-2"></div>
        </motion.div>
      </motion.div>
    </section>
  );
}