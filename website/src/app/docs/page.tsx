'use client';

import { motion } from 'framer-motion';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function DocsPage() {
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
            <h1 className="heading-lg text-gray-900 mb-6">Documentation</h1>
            <p className="text-large text-gray-600">
              Comprehensive guides and API references to help you integrate ReliQuary into your applications.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Getting Started</h3>
              <p className="text-gray-600 mb-4">
                Learn how to set up your ReliQuary account and make your first API calls.
              </p>
              <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
                Read Guide →
              </a>
            </div>
            
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">API Reference</h3>
              <p className="text-gray-600 mb-4">
                Detailed documentation for all API endpoints, parameters, and response formats.
              </p>
              <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
                View API Docs →
              </a>
            </div>
            
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">SDKs</h3>
              <p className="text-gray-600 mb-4">
                Language-specific libraries and examples for Python, JavaScript, Java, and Go.
              </p>
              <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
                Browse SDKs →
              </a>
            </div>
          </div>
          
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Popular Topics</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="border border-gray-200 rounded-lg p-6 hover:border-primary-300 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-2">Authentication</h3>
                <p className="text-gray-600 text-sm">
                  Learn how to authenticate API requests using OAuth 2.0 and JWT tokens.
                </p>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6 hover:border-primary-300 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-2">Vault Management</h3>
                <p className="text-gray-600 text-sm">
                  Create, update, and manage encrypted vaults for secure data storage.
                </p>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6 hover:border-primary-300 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-2">Context Verification</h3>
                <p className="text-gray-600 text-sm">
                  Implement zero-knowledge context verification for enhanced security.
                </p>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6 hover:border-primary-300 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-2">Trust Scoring</h3>
                <p className="text-gray-600 text-sm">
                  Understand how dynamic trust scores are calculated and enforced.
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