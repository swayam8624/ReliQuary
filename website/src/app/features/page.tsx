'use client';

import { motion } from 'framer-motion';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function FeaturesPage() {
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
            <h1 className="heading-lg text-gray-900 mb-6">Core Features</h1>
            <p className="text-large text-gray-600">
              Advanced cryptographic capabilities designed for the quantum computing era.
            </p>
          </div>
          
          <div className="space-y-12">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Post-Quantum Cryptography</h2>
                <p className="text-gray-600 mb-4">
                  Our platform implements cutting-edge post-quantum cryptographic algorithms including 
                  Kyber for key encapsulation and Falcon for digital signatures, ensuring your data 
                  remains secure even against quantum computing threats.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">Kyber key encapsulation mechanism</span>
                  </li>
                  <li className="flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">Falcon digital signature scheme</span>
                  </li>
                  <li className="flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">AES-GCM symmetric encryption</span>
                  </li>
                </ul>
              </div>
              <div className="bg-gray-100 rounded-xl p-8 h-64 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">🔐</div>
                  <p className="text-gray-600">Cryptographic Visualization</p>
                </div>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div className="bg-gray-100 rounded-xl p-8 h-64 flex items-center justify-center md:order-2">
                <div className="text-center">
                  <div className="text-4xl mb-2">🧮</div>
                  <p className="text-gray-600">Zero-Knowledge Proofs</p>
                </div>
              </div>
              <div className="md:order-1">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Zero-Knowledge Proofs</h2>
                <p className="text-gray-600 mb-4">
                  Verify context and authenticity without revealing sensitive information. Our 
                  implementation uses Circom circuits and SnarkJS for efficient privacy-preserving 
                  verification of device fingerprints, timestamps, locations, and access patterns.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">Device fingerprint verification</span>
                  </li>
                  <li className="flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">Timestamp validation</span>
                  </li>
                  <li className="flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">Location chain verification</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
}