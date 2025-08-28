'use client';

import { motion } from 'framer-motion';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function ProductPage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      <main className="pt-24 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="container-custom"
        >
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h1 className="heading-lg text-gray-900 mb-6">Product Overview</h1>
            <p className="text-large text-gray-600">
              Discover the powerful features that make ReliQuary the most advanced cryptographic memory platform.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Post-Quantum Security</h3>
              <p className="text-gray-600">
                Built with quantum-resistant algorithms to protect your data against future threats.
              </p>
            </div>
            
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Zero-Knowledge Proofs</h3>
              <p className="text-gray-600">
                Verify context without revealing sensitive information for enhanced privacy.
              </p>
            </div>
            
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Multi-Agent Consensus</h3>
              <p className="text-gray-600">
                Intelligent decision-making system with Byzantine Fault-Tolerant algorithms.
              </p>
            </div>
          </div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
}