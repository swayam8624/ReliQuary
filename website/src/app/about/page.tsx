'use client';

import { motion } from 'framer-motion';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function AboutPage() {
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
            <h1 className="heading-lg text-gray-900 dark:text-white mb-6">About ReliQuary</h1>
            <p className="text-large text-gray-600 dark:text-gray-300">
              Pioneering the future of cryptographic security in the quantum computing era.
            </p>
          </div>
          
          <div className="prose prose-lg max-w-none dark:prose-invert">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Our Mission</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                At ReliQuary, we're committed to building the most secure and intelligent cryptographic 
                infrastructure for the post-quantum world. Our mission is to protect digital assets 
                against both current and future threats through innovative cryptography, zero-knowledge 
                proofs, and multi-agent consensus systems.
              </p>
              <p className="text-gray-700 dark:text-gray-300">
                We believe that security should be both impenetrable and intelligent, adapting to 
                context and behavior patterns to provide dynamic protection that evolves with threats.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-12 mb-16">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Our Approach</h2>
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    </div>
                    <p className="ml-4 text-gray-700 dark:text-gray-300">
                      <span className="font-semibold">Post-Quantum Security:</span> Implementing 
                      quantum-resistant algorithms to future-proof your data
                    </p>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    </div>
                    <p className="ml-4 text-gray-700 dark:text-gray-300">
                      <span className="font-semibold">Context-Aware Protection:</span> Using 
                      zero-knowledge proofs to verify without revealing sensitive information
                    </p>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    </div>
                    <p className="ml-4 text-gray-700 dark:text-gray-300">
                      <span className="font-semibold">Intelligent Consensus:</span> Multi-agent 
                      decision making with Byzantine Fault-Tolerant algorithms
                    </p>
                  </li>
                </ul>
              </div>
              
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Core Values</h2>
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    </div>
                    <p className="ml-4 text-gray-700 dark:text-gray-300">
                      <span className="font-semibold">Security First:</span> Every decision we make 
                      prioritizes the protection of your data
                    </p>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    </div>
                    <p className="ml-4 text-gray-700 dark:text-gray-300">
                      <span className="font-semibold">Innovation:</span> Continuously pushing the 
                      boundaries of cryptographic research
                    </p>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    </div>
                    <p className="ml-4 text-gray-700 dark:text-gray-300">
                      <span className="font-semibold">Transparency:</span> Open about our methods 
                      and committed to open-source principles
                    </p>
                  </li>
                </ul>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl p-8 text-white">
              <h2 className="text-2xl font-bold mb-4">Join Us in Securing the Future</h2>
              <p className="mb-6 opacity-90">
                We're always looking for talented cryptographers, security researchers, and engineers 
                who share our passion for building impenetrable security solutions. If you're excited 
                about post-quantum cryptography, zero-knowledge proofs, or distributed systems, we'd 
                love to hear from you.
              </p>
              <a 
                href="/careers" 
                className="inline-block bg-white text-primary-600 font-semibold py-3 px-6 rounded-lg hover:bg-gray-100 transition-colors"
              >
                View Open Positions
              </a>
            </div>
          </div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
}