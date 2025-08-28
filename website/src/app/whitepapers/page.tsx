'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  DocumentTextIcon, 
  AcademicCapIcon, 
  BookOpenIcon,
  ArrowDownTrayIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const whitepapers = [
  {
    id: 1,
    title: 'Post-Quantum Cryptography Migration Guide',
    description: 'A comprehensive guide to transitioning your systems to post-quantum cryptographic algorithms, including practical implementation strategies and risk assessment frameworks.',
    author: 'Dr. Emily Rodriguez',
    date: 'May 15, 2024',
    pages: 42,
    category: 'Security',
    downloads: '1,248',
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 2,
    title: 'Zero-Knowledge Proofs in Enterprise Applications',
    description: 'Exploring practical implementations of zero-knowledge proofs for privacy-preserving applications in enterprise environments, with real-world case studies.',
    author: 'Prof. James Wilson',
    date: 'April 28, 2024',
    pages: 36,
    category: 'Development',
    downloads: '987',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 3,
    title: 'Multi-Agent Consensus Systems: Architecture and Implementation',
    description: 'Detailed analysis of distributed consensus mechanisms using autonomous agents, including performance benchmarks and fault tolerance characteristics.',
    author: 'Dr. Sarah Kim',
    date: 'April 12, 2024',
    pages: 58,
    category: 'Architecture',
    downloads: '1,532',
    image: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 4,
    title: 'Threshold Cryptography for Distributed Trust',
    description: 'Implementing threshold cryptographic schemes to eliminate single points of failure and distribute trust across multiple parties in enterprise systems.',
    author: 'Dr. Michael Thompson',
    date: 'March 30, 2024',
    pages: 47,
    category: 'Security',
    downloads: '1,102',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 5,
    title: 'Distributed Key Management in Cloud Environments',
    description: 'Best practices for managing cryptographic keys in distributed cloud environments, including air-gapped storage and automated rotation strategies.',
    author: 'Prof. David Chen',
    date: 'March 15, 2024',
    pages: 39,
    category: 'Infrastructure',
    downloads: '876',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 6,
    title: 'Quantum-Resistant Algorithms: Kyber and Falcon Implementation',
    description: 'Technical deep-dive into implementing NIST-standardized post-quantum algorithms Kyber and Falcon, with performance benchmarks and optimization techniques.',
    author: 'Dr. Anna Petrova',
    date: 'February 28, 2024',
    pages: 64,
    category: 'Research',
    downloads: '2,105',
    image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  }
];

const categories = [
  { name: 'All', count: 24 },
  { name: 'Security', count: 8 },
  { name: 'Development', count: 4 },
  { name: 'Architecture', count: 5 },
  { name: 'Infrastructure', count: 3 },
  { name: 'Research', count: 4 }
];

export default function WhitepapersPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="hero-bg py-16 lg:py-24">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="heading-xl text-gray-900 dark:text-white mb-6">
                Research Whitepapers
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                In-depth technical research and analysis on cryptographic innovations, 
                distributed systems, and the future of digital security.
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="py-8 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="container-custom">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.name}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  category.name === 'All'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {category.name} ({category.count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Whitepapers */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {whitepapers.map((paper, index) => (
              <motion.div
                key={paper.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="h-48 overflow-hidden">
                  <img 
                    src={paper.image} 
                    alt={paper.title} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/50 text-primary-800 dark:text-primary-200">
                      {paper.category}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {paper.pages} pages
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    {paper.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {paper.description}
                  </p>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-4">
                    <AcademicCapIcon className="h-4 w-4 mr-2" />
                    <span>{paper.author}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-6">
                    <span>{paper.date}</span>
                    <span>{paper.downloads} downloads</span>
                  </div>
                  <div className="flex space-x-3">
                    <button className="flex-1 btn-primary flex items-center justify-center">
                      <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                      Download
                    </button>
                    <Link 
                      href={`/whitepapers/${paper.id}`}
                      className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center justify-center"
                    >
                      <BookOpenIcon className="h-5 w-5 mr-2" />
                      Read
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-center mt-12">
            <nav className="flex items-center space-x-2">
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                Previous
              </button>
              <button className="px-4 py-2 rounded-lg bg-primary-500 text-white">
                1
              </button>
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                2
              </button>
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                Next
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* Research Collaboration */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex p-3 rounded-lg bg-primary-500 text-white mb-6">
              <AcademicCapIcon className="h-8 w-8" />
            </div>
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Academic Collaboration
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
              We collaborate with leading universities and research institutions to advance 
              the field of cryptographic security and distributed systems.
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
              {[
                'MIT', 'Stanford', 'CMU', 'Berkeley',
                'Oxford', 'Cambridge', 'ETH Zurich', 'NTU Singapore'
              ].map((institution, index) => (
                <div 
                  key={index} 
                  className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 shadow-sm"
                >
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {institution}
                  </div>
                </div>
              ))}
            </div>
            
            <Link 
              href="/research" 
              className="btn-outline inline-flex items-center"
            >
              Learn About Our Research
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Newsletter Signup */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-3xl mx-auto bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl p-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Get New Research Delivered
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Subscribe to receive our latest whitepapers and research findings directly to your inbox.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-grow px-4 py-3 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-gray-900"
              />
              <button className="px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors">
                Subscribe
              </button>
            </div>
            
            <p className="text-primary-200 text-sm mt-4">
              We respect your privacy. Unsubscribe at any time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}