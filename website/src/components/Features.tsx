'use client';

import { useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { 
  ShieldCheckIcon,
  CpuChipIcon,
  EyeSlashIcon,
  CloudArrowUpIcon,
  LockClosedIcon,
  UsersIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ServerIcon,
  GlobeAltIcon,
  BoltIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const features = [
  {
    icon: ShieldCheckIcon,
    title: 'Post-Quantum Cryptography',
    description: 'Future-proof security with Kyber and Falcon algorithms that resist quantum computer attacks.',
    details: [
      'NIST-approved post-quantum algorithms',
      'Hybrid classical-quantum security',
      'Automatic algorithm selection',
      'Future-proof migration path'
    ],
    color: 'blue'
  },
  {
    icon: CpuChipIcon,
    title: 'Multi-Agent Consensus',
    description: 'Distributed decision-making with Byzantine fault-tolerant consensus across multiple agents.',
    details: [
      'Byzantine fault tolerance',
      'Specialized agent roles',
      'Intelligent decision orchestration',
      'Real-time consensus monitoring'
    ],
    color: 'purple'
  },
  {
    icon: EyeSlashIcon,
    title: 'Zero-Knowledge Proofs',
    description: 'Verify credentials and context without revealing sensitive information.',
    details: [
      'Privacy-preserving verification',
      'Context-aware authentication',
      'Selective disclosure protocols',
      'Compliance-ready proofs'
    ],
    color: 'green'
  },
  {
    icon: CloudArrowUpIcon,
    title: 'Enterprise Scalability',
    description: 'Production-grade infrastructure that scales from startups to Fortune 500 companies.',
    details: [
      'Auto-scaling architecture',
      'Global deployment options',
      'Multi-tenant isolation',
      '99.99% uptime SLA'
    ],
    color: 'orange'
  },
  {
    icon: LockClosedIcon,
    title: 'Threshold Cryptography',
    description: 'Distribute cryptographic operations across multiple parties for enhanced security.',
    details: [
      'Secret sharing protocols',
      'Multi-party computation',
      'Distributed key generation',
      'Collusion resistance'
    ],
    color: 'red'
  },
  {
    icon: UsersIcon,
    title: 'Identity Management',
    description: 'Complete identity lifecycle management with DIDs and verifiable credentials.',
    details: [
      'Decentralized identifiers (DIDs)',
      'Verifiable credentials',
      'SSO integration',
      'Role-based access control'
    ],
    color: 'indigo'
  }
];

const useCases = [
  {
    icon: ServerIcon,
    title: 'Financial Services',
    description: 'Secure transactions, regulatory compliance, and risk management.',
    benefits: ['PCI DSS compliance', 'Fraud detection', 'Regulatory reporting']
  },
  {
    icon: GlobeAltIcon,
    title: 'Healthcare',
    description: 'Patient data protection, HIPAA compliance, and secure research.',
    benefits: ['HIPAA compliance', 'Patient privacy', 'Secure data sharing']
  },
  {
    icon: BoltIcon,
    title: 'Government',
    description: 'National security, citizen services, and secure communications.',
    benefits: ['FISMA compliance', 'Secure communications', 'Digital identity']
  },
  {
    icon: Cog6ToothIcon,
    title: 'Enterprise',
    description: 'Data protection, secure collaboration, and compliance management.',
    benefits: ['Data sovereignty', 'Zero-trust security', 'Audit trails']
  }
];

const metrics = [
  { value: '10M+', label: 'Operations/Second', description: 'High-performance cryptographic operations' },
  { value: '< 200ms', label: 'Average Latency', description: 'Lightning-fast response times' },
  { value: '256-bit', label: 'Quantum Security', description: 'Post-quantum encryption strength' },
  { value: '99.99%', label: 'Availability', description: 'Enterprise-grade reliability' }
];

export default function Features() {
  const [activeFeature, setActiveFeature] = useState(0);
  const [activeTab, setActiveTab] = useState<'features' | 'usecases' | 'metrics'>('features');
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <section id="features" className="section-padding bg-white" ref={ref}>
      <div className="container-custom">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <h2 className="heading-lg text-gray-900 mb-6">
            Comprehensive Security Platform
          </h2>
          <p className="text-large text-gray-600">
            Built for the quantum computing era with enterprise-grade security, 
            scalability, and intelligent automation.
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex justify-center mb-12"
        >
          <div className="inline-flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('features')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'features'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Core Features
            </button>
            <button
              onClick={() => setActiveTab('usecases')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'usecases'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Use Cases
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'metrics'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Performance
            </button>
          </div>
        </motion.div>

        {/* Core Features Tab */}
        {activeTab === 'features' && (
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            
            {/* Feature List */}
            <div className="space-y-4">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className={`p-6 rounded-xl cursor-pointer transition-all ${
                    activeFeature === index
                      ? 'bg-primary-50 border-2 border-primary-200'
                      : 'bg-gray-50 border-2 border-transparent hover:border-gray-200'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-lg ${
                      feature.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                      feature.color === 'purple' ? 'bg-purple-100 text-purple-600' :
                      feature.color === 'green' ? 'bg-green-100 text-green-600' :
                      feature.color === 'orange' ? 'bg-orange-100 text-orange-600' :
                      feature.color === 'red' ? 'bg-red-100 text-red-600' :
                      'bg-indigo-100 text-indigo-600'
                    }`}>
                      <feature.icon className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600 mb-3">
                        {feature.description}
                      </p>
                      {activeFeature === index && (
                        <motion.ul
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          transition={{ duration: 0.3 }}
                          className="space-y-2"
                        >
                          {feature.details.map((detail, detailIndex) => (
                            <li key={detailIndex} className="flex items-center space-x-2">
                              <CheckCircleIcon className="h-4 w-4 text-green-500" />
                              <span className="text-sm text-gray-700">{detail}</span>
                            </li>
                          ))}
                        </motion.ul>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Feature Visualization */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="lg:sticky lg:top-24"
            >
              <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 text-white">
                <div className="mb-6">
                  <div className={`inline-flex p-3 rounded-lg mb-4 ${
                    features[activeFeature].color === 'blue' ? 'bg-blue-500' :
                    features[activeFeature].color === 'purple' ? 'bg-purple-500' :
                    features[activeFeature].color === 'green' ? 'bg-green-500' :
                    features[activeFeature].color === 'orange' ? 'bg-orange-500' :
                    features[activeFeature].color === 'red' ? 'bg-red-500' :
                    'bg-indigo-500'
                  }`}>
                    {React.createElement(features[activeFeature].icon, { className: "h-8 w-8" })}
                  </div>
                  <h3 className="text-2xl font-bold mb-2">
                    {features[activeFeature].title}
                  </h3>
                  <p className="text-gray-300">
                    {features[activeFeature].description}
                  </p>
                </div>

                {/* Code Example */}
                <div className="bg-black rounded-lg p-4 font-mono text-sm">
                  <div className="flex items-center space-x-2 mb-3">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-gray-400 ml-4 text-xs">
                      {features[activeFeature].title.toLowerCase().replace(/\s+/g, '-')}.py
                    </span>
                  </div>
                  <pre className="text-green-400 text-xs overflow-x-auto">
{activeFeature === 0 && `# Post-Quantum Cryptography
from reliquary import PostQuantumVault

vault = PostQuantumVault()
encrypted = vault.encrypt(
    data="sensitive_information",
    algorithm="kyber-1024"
)
print(f"Quantum-safe: {encrypted}")`}

{activeFeature === 1 && `# Multi-Agent Consensus
from reliquary import ConsensusEngine

engine = ConsensusEngine(agents=4)
decision = engine.decide(
    proposal="access_request",
    threshold=0.75
)
print(f"Consensus: {decision.approved}")`}

{activeFeature === 2 && `# Zero-Knowledge Proofs
from reliquary import ZKProofSystem

zk = ZKProofSystem()
proof = zk.generate_proof(
    statement="age >= 18",
    private_data={"age": 25}
)
print(f"Proof valid: {zk.verify(proof)}")`}

{activeFeature === 3 && `# Enterprise Scalability
from reliquary import EnterpriseVault

vault = EnterpriseVault(
    auto_scale=True,
    regions=["us-east", "eu-west"]
)
status = vault.health_check()
print(f"Uptime: {status.uptime_pct}%")`}

{activeFeature === 4 && `# Threshold Cryptography
from reliquary import ThresholdCrypto

tc = ThresholdCrypto(n=5, k=3)
shares = tc.split_secret("secret_key")
reconstructed = tc.reconstruct(
    shares[:3]  # Any 3 of 5 shares
)
print(f"Secret recovered: {reconstructed}")`}

{activeFeature === 5 && `# Identity Management
from reliquary import IdentityManager

im = IdentityManager()
did = im.create_identity(
    attributes=["name", "email"],
    verifiable=True
)
print(f"DID created: {did.identifier}")`}
                  </pre>
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Use Cases Tab */}
        {activeTab === 'usecases' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="grid md:grid-cols-2 gap-8"
          >
            {useCases.map((useCase, index) => (
              <div key={index} className="card">
                <div className="flex items-start space-x-4">
                  <div className="p-3 bg-primary-100 text-primary-600 rounded-lg">
                    <useCase.icon className="h-8 w-8" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {useCase.title}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {useCase.description}
                    </p>
                    <div className="space-y-2">
                      {useCase.benefits.map((benefit, benefitIndex) => (
                        <div key={benefitIndex} className="flex items-center space-x-2">
                          <CheckCircleIcon className="h-4 w-4 text-green-500" />
                          <span className="text-sm text-gray-700">{benefit}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {/* Performance Metrics Tab */}
        {activeTab === 'metrics' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {metrics.map((metric, index) => (
              <div key={index} className="text-center">
                <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl p-8 text-white mb-4">
                  <div className="text-3xl font-bold mb-2">{metric.value}</div>
                  <div className="text-primary-100">{metric.label}</div>
                </div>
                <p className="text-gray-600">{metric.description}</p>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </section>
  );
}