'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRightIcon, ShieldCheckIcon, CpuChipIcon, LightBulbIcon, LockClosedIcon } from '@heroicons/react/24/outline';

export default function Hero() {
  return (
    <section className="hero-bg dark:bg-gray-900 pt-24 pb-16 lg:pt-32 lg:pb-24">
      <div className="container-custom">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center px-4 py-2 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-sm font-medium mb-6">
              <LightBulbIcon className="h-4 w-4 mr-2" />
              First of its kind cryptographic platform
            </div>
            
            <h1 className="heading-xl text-gray-900 dark:text-white mb-6">
              The World's First{' '}
              <span className="gradient-text dark:text-transparent">Post-Quantum</span>{' '}
              Memory Vault
            </h1>
            
            <p className="text-large text-gray-600 dark:text-gray-300 mb-8">
              Secure your digital assets against today's threats and tomorrow's quantum computers. 
              Built with military-grade cryptography, zero-knowledge proofs, and intelligent 
              multi-agent consensus for unparalleled protection.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Link 
                href="/signup" 
                className="btn-primary text-center"
              >
                Start Free Trial
              </Link>
              <Link 
                href="/demo" 
                className="btn-secondary text-center dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700"
              >
                <span>View Demo</span>
                <ArrowRightIcon className="h-5 w-5 ml-2" />
              </Link>
            </div>
            
            <div className="grid grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white">PQC</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Post-Quantum</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white">ZK</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Zero-Knowledge</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white">BFT</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Byzantine Fault-Tolerant</div>
              </div>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">reliquary.io</div>
              </div>
              
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0 mt-1">
                    <ShieldCheckIcon className="h-6 w-6 text-primary-500" />
                  </div>
                  <div className="ml-4">
                    <div className="font-medium text-gray-900 dark:text-white">Secure Vault Created</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Encrypted with post-quantum algorithms</div>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 mt-1">
                    <LockClosedIcon className="h-6 w-6 text-primary-500" />
                  </div>
                  <div className="ml-4">
                    <div className="font-medium text-gray-900 dark:text-white">Context Verified</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Zero-knowledge proof validated</div>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 mt-1">
                    <CpuChipIcon className="h-6 w-6 text-primary-500" />
                  </div>
                  <div className="ml-4">
                    <div className="font-medium text-gray-900 dark:text-white">Access Granted</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Multi-agent consensus achieved</div>
                  </div>
                </div>
                
                <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">Trust Score</div>
                    <div className="text-sm font-bold text-gray-900 dark:text-white">92.5/100</div>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-2">
                    <div 
                      className="bg-gradient-to-r from-primary-500 to-accent-500 h-3 rounded-full" 
                      style={{ width: '92.5%' }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>Low</span>
                    <span className="font-medium">Excellent</span>
                    <span>High</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="absolute -top-6 -right-6 w-24 h-24 bg-primary-500 rounded-full opacity-20 blur-3xl"></div>
            <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-accent-500 rounded-full opacity-20 blur-3xl"></div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}