'use client';

import { motion } from 'framer-motion';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Header />
      
      <main className="pt-24 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="container-custom"
        >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h1 className="heading-lg text-gray-900 dark:text-white mb-6">Enterprise Security</h1>
            <p className="text-large text-gray-600 dark:text-gray-300">
              Military-grade cryptographic protection with post-quantum security and zero-knowledge verification.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8 mb-16">
            <div className="card dark:bg-gray-800">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-6">
                <div className="text-2xl">🔐</div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Post-Quantum Cryptography</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Protected against future quantum computing threats with Kyber key encapsulation 
                and Falcon digital signatures.
              </p>
            </div>
            
            <div className="card dark:bg-gray-800">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-6">
                <div className="text-2xl">👁️</div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Zero-Knowledge Proofs</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Verify context and authenticity without revealing sensitive information through 
                advanced ZK-SNARK implementations.
              </p>
            </div>
            
            <div className="card dark:bg-gray-800">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-6">
                <div className="text-2xl">🤖</div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Multi-Agent Consensus</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Byzantine Fault-Tolerant decision making with specialized agent nodes for intelligent 
                access control.
              </p>
            </div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 mb-16">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Compliance & Certifications</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-6 bg-white dark:bg-gray-700 rounded-lg">
                <div className="text-3xl mb-3">🛡️</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">SOC 2 Type II</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Security and availability</p>
              </div>
              
              <div className="text-center p-6 bg-white dark:bg-gray-700 rounded-lg">
                <div className="text-3xl mb-3">📜</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">ISO 27001</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Information security management</p>
              </div>
              
              <div className="text-center p-6 bg-white dark:bg-gray-700 rounded-lg">
                <div className="text-3xl mb-3">🔒</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">FIPS 140-2</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cryptographic modules</p>
              </div>
              
              <div className="text-center p-6 bg-white dark:bg-gray-700 rounded-lg">
                <div className="text-3xl mb-3">🇪🇺</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">GDPR Compliant</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Data protection regulation</p>
              </div>
            </div>
          </div>
          
          <div className="prose prose-lg max-w-none dark:prose-invert">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Security Architecture</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              ReliQuary's security architecture is built on multiple layers of protection, each 
              designed to defend against different types of threats:
            </p>
            
            <div className="space-y-8">
              <div className="border-l-4 border-primary-500 pl-6 py-2">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Layer 1: Cryptographic Foundation</h3>
                <p className="text-gray-700 dark:text-gray-300">
                  All data is encrypted using post-quantum algorithms that are resistant to both 
                  classical and quantum computer attacks. We implement Kyber for key encapsulation 
                  and Falcon for digital signatures, both of which are finalists in the NIST 
                  Post-Quantum Cryptography Standardization process.
                </p>
              </div>
              
              <div className="border-l-4 border-primary-500 pl-6 py-2">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Layer 2: Zero-Knowledge Verification</h3>
                <p className="text-gray-700 dark:text-gray-300">
                  Context verification is performed using zero-knowledge proofs, ensuring that 
                  authentication and authorization decisions can be made without exposing sensitive 
                  information. Our Circom-based circuits verify device fingerprints, timestamps, 
                  locations, and access patterns without revealing the underlying data.
                </p>
              </div>
              
              <div className="border-l-4 border-primary-500 pl-6 py-2">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Layer 3: Multi-Agent Consensus</h3>
                <p className="text-gray-700 dark:text-gray-300">
                  Access decisions are made through a Byzantine Fault-Tolerant multi-agent system 
                  that evaluates requests from multiple perspectives. Specialized agents (Neutral, 
                  Permissive, Strict, and Watchdog) collaborate to make intelligent decisions based 
                  on context, trust scores, and historical behavior patterns.
                </p>
              </div>
              
              <div className="border-l-4 border-primary-500 pl-6 py-2">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Layer 4: Immutable Audit Trail</h3>
                <p className="text-gray-700 dark:text-gray-300">
                  All security events are logged to an immutable Merkle tree-based audit trail that 
                  provides cryptographic proof of system integrity. Logs are tamper-evident and can 
                  be independently verified by third parties.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
}