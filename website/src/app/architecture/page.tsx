'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ServerIcon, 
  LockClosedIcon, 
  ArrowsRightLeftIcon,
  CubeIcon,
  CpuChipIcon,
  ArrowPathIcon,
  ShieldCheckIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

const architectureComponents = [
  {
    id: 'core',
    title: 'Core Cryptographic Engine',
    description: 'The heart of ReliQuary featuring post-quantum cryptographic algorithms including Kyber for key encapsulation and Falcon for digital signatures.',
    icon: LockClosedIcon,
    features: [
      'Post-quantum security with NIST-standardized algorithms',
      'Hardware-accelerated cryptographic operations',
      'Zero-knowledge proof generation and verification',
      'Threshold cryptography for distributed trust'
    ]
  },
  {
    id: 'consensus',
    title: 'Multi-Agent Consensus System',
    description: 'Distributed consensus mechanism using autonomous agents that validate and secure transactions without central authority.',
    icon: ArrowsRightLeftIcon,
    features: [
      'Byzantine fault-tolerant consensus',
      'Adaptive consensus based on network conditions',
      'Cross-chain interoperability protocols',
      'Real-time consensus finality tracking'
    ]
  },
  {
    id: 'storage',
    title: 'Distributed Storage Network',
    description: 'Secure, decentralized storage with built-in redundancy and encryption at rest.',
    icon: ServerIcon,
    features: [
      'Sharded storage with geographic distribution',
      'End-to-end encryption with client-side keys',
      'Automatic backup and recovery mechanisms',
      'Content-addressable storage with deduplication'
    ]
  },
  {
    id: 'intelligence',
    title: 'AI-ML Intelligence Layer',
    description: 'Machine learning algorithms that enhance security, optimize performance, and detect anomalies.',
    icon: CpuChipIcon,
    features: [
      'Anomaly detection for security threats',
      'Performance optimization through predictive analytics',
      'Automated security patch deployment',
      'Intelligent resource allocation'
    ]
  },
  {
    id: 'api',
    title: 'API Gateway & Services',
    description: 'Comprehensive API ecosystem with rate limiting, authentication, and real-time monitoring.',
    icon: CubeIcon,
    features: [
      'RESTful and GraphQL APIs',
      'Real-time WebSocket connections',
      'OAuth 2.0 and JWT authentication',
      'Rate limiting and DDoS protection'
    ]
  },
  {
    id: 'observability',
    title: 'Observability & Monitoring',
    description: 'Full-stack observability with real-time metrics, logs, and distributed tracing.',
    icon: ArrowPathIcon,
    features: [
      'Real-time performance dashboards',
      'Distributed tracing with OpenTelemetry',
      'Automated alerting and incident response',
      'Comprehensive audit logging'
    ]
  }
];

export default function ArchitecturePage() {
  const [selectedComponent, setSelectedComponent] = useState('core');

  const currentComponent = architectureComponents.find(comp => comp.id === selectedComponent) || architectureComponents[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="hero-bg py-16 lg:py-24">
        <div className="container-custom text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="heading-xl text-gray-900 dark:text-white mb-6">
              Enterprise-Grade Architecture
            </h1>
            <p className="text-xl text-gray-700 dark:text-gray-300 max-w-3xl mx-auto mb-10">
              Built from the ground up with security, scalability, and reliability as core principles. 
              Our architecture combines cutting-edge cryptography with distributed systems for unparalleled performance.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <div className="flex items-center text-gray-600 dark:text-gray-400">
                <ShieldCheckIcon className="h-5 w-5 mr-2 text-green-500" />
                <span>Post-Quantum Secure</span>
              </div>
              <div className="flex items-center text-gray-600 dark:text-gray-400">
                <LightBulbIcon className="h-5 w-5 mr-2 text-blue-500" />
                <span>AI-Enhanced Security</span>
              </div>
              <div className="flex items-center text-gray-600 dark:text-gray-400">
                <ServerIcon className="h-5 w-5 mr-2 text-purple-500" />
                <span>99.99% Uptime SLA</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Architecture Diagram Section */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              System Architecture Overview
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Our platform is designed as a modular, distributed system with security and scalability at its core.
            </p>
          </div>

          {/* Interactive Architecture Diagram */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 mb-16">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column */}
              <div className="space-y-6">
                <motion.div 
                  className={`p-6 rounded-xl cursor-pointer transition-all duration-300 ${
                    selectedComponent === 'storage' 
                      ? 'bg-primary-500 text-white shadow-lg' 
                      : 'bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={() => setSelectedComponent('storage')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <ServerIcon className="h-8 w-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Storage Network</h3>
                  <p className="text-sm opacity-80">Distributed, encrypted storage</p>
                </motion.div>

                <motion.div 
                  className={`p-6 rounded-xl cursor-pointer transition-all duration-300 ${
                    selectedComponent === 'intelligence' 
                      ? 'bg-primary-500 text-white shadow-lg' 
                      : 'bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={() => setSelectedComponent('intelligence')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <CpuChipIcon className="h-8 w-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">AI-ML Layer</h3>
                  <p className="text-sm opacity-80">Intelligent security & optimization</p>
                </motion.div>
              </div>

              {/* Center Column */}
              <div className="flex flex-col justify-center items-center">
                <motion.div 
                  className={`p-8 rounded-2xl cursor-pointer transition-all duration-300 w-full text-center ${
                    selectedComponent === 'core' 
                      ? 'bg-primary-500 text-white shadow-xl' 
                      : 'bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={() => setSelectedComponent('core')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <LockClosedIcon className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-xl font-bold mb-2">Core Engine</h3>
                  <p className="opacity-80">Cryptographic operations</p>
                </motion.div>
              </div>

              {/* Right Column */}
              <div className="space-y-6">
                <motion.div 
                  className={`p-6 rounded-xl cursor-pointer transition-all duration-300 ${
                    selectedComponent === 'api' 
                      ? 'bg-primary-500 text-white shadow-lg' 
                      : 'bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={() => setSelectedComponent('api')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <CubeIcon className="h-8 w-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">API Services</h3>
                  <p className="text-sm opacity-80">Developer interfaces</p>
                </motion.div>

                <motion.div 
                  className={`p-6 rounded-xl cursor-pointer transition-all duration-300 ${
                    selectedComponent === 'observability' 
                      ? 'bg-primary-500 text-white shadow-lg' 
                      : 'bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={() => setSelectedComponent('observability')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <ArrowPathIcon className="h-8 w-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Monitoring</h3>
                  <p className="text-sm opacity-80">Observability & analytics</p>
                </motion.div>
              </div>
            </div>

            {/* Bottom Row */}
            <div className="mt-8 flex justify-center">
              <motion.div 
                className={`p-6 rounded-xl cursor-pointer transition-all duration-300 max-w-md ${
                  selectedComponent === 'consensus' 
                    ? 'bg-primary-500 text-white shadow-lg' 
                    : 'bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
                onClick={() => setSelectedComponent('consensus')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <ArrowsRightLeftIcon className="h-8 w-8 mx-auto mb-3" />
                <h3 className="text-lg font-semibold mb-2 text-center">Consensus System</h3>
                <p className="text-sm opacity-80 text-center">Multi-agent validation</p>
              </motion.div>
            </div>
          </div>

          {/* Component Details */}
          <motion.div 
            key={currentComponent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8"
          >
            <div className="flex items-start mb-6">
              <currentComponent.icon className="h-10 w-10 text-primary-500 mr-4 flex-shrink-0" />
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{currentComponent.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 mt-2">{currentComponent.description}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentComponent.features.map((feature, index) => (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center mr-3 mt-0.5">
                    <div className="h-2 w-2 rounded-full bg-primary-500"></div>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">{feature}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Security Features */}
      <div className="py-16 lg:py-24 bg-gradient-to-r from-primary-500 to-accent-500 text-white">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-white mb-4">
              Security-First Design
            </h2>
            <p className="text-xl text-primary-100 max-w-3xl mx-auto">
              Every component is designed with security as the primary concern, implementing defense-in-depth principles.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: 'Zero-Knowledge Proofs',
                description: 'All transactions can be verified without revealing sensitive data',
                icon: ShieldCheckIcon
              },
              {
                title: 'Post-Quantum Cryptography',
                description: 'NIST-standardized algorithms resistant to quantum computer attacks',
                icon: LockClosedIcon
              },
              {
                title: 'Continuous Monitoring',
                description: '24/7 threat detection with AI-powered anomaly identification',
                icon: ArrowPathIcon
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
              >
                <feature.icon className="h-10 w-10 text-white mb-4" />
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-primary-100">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Scalability Section */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Built for Scale
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Our architecture automatically scales to meet your demands while maintaining performance and security.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Horizontal Scaling Architecture
              </h3>
              <ul className="space-y-4">
                {[
                  'Auto-scaling microservices',
                  'Load-balanced API gateways',
                  'Distributed storage clusters',
                  'Elastic compute resources',
                  'Global CDN integration',
                  'Database sharding and replication'
                ].map((item, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center mr-3 mt-0.5">
                      <div className="h-2 w-2 rounded-full bg-primary-500"></div>
                    </div>
                    <span className="text-gray-700 dark:text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl p-8">
              <div className="space-y-6">
                <div className="flex justify-between items-center pb-4 border-b border-gray-200 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-400">API Throughput</span>
                  <span className="font-semibold text-gray-900 dark:text-white">1M req/sec</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-gray-200 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-400">Storage Capacity</span>
                  <span className="font-semibold text-gray-900 dark:text-white">100 PB</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-gray-200 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-400">Global Regions</span>
                  <span className="font-semibold text-gray-900 dark:text-white">25+</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Uptime SLA</span>
                  <span className="font-semibold text-gray-900 dark:text-white">99.99%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}