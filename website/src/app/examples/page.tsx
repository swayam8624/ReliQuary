'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  CodeBracketIcon, 
  LightBulbIcon, 
  CommandLineIcon,
  ArrowRightIcon,
  StarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

const examples = [
  {
    id: 1,
    title: 'Secure Document Signing',
    description: 'Implementation of digital signatures using post-quantum Falcon algorithm for legally binding document authentication.',
    language: 'JavaScript',
    framework: 'Node.js',
    difficulty: 'Intermediate',
    stars: 42,
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 2,
    title: 'Zero-Knowledge Identity Verification',
    description: 'Privacy-preserving identity verification system that proves attributes without revealing personal information.',
    language: 'Python',
    framework: 'Flask',
    difficulty: 'Advanced',
    stars: 78,
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 3,
    title: 'Multi-Agent Consensus Network',
    description: 'Distributed consensus system using autonomous agents to validate transactions without central authority.',
    language: 'Go',
    framework: 'Gin',
    difficulty: 'Expert',
    stars: 124,
    image: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 4,
    title: 'Encrypted Data Storage',
    description: 'Client-side encryption with threshold cryptography for secure data storage and sharing.',
    language: 'TypeScript',
    framework: 'React',
    difficulty: 'Advanced',
    stars: 96,
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 5,
    title: 'Quantum-Resistant Key Exchange',
    description: 'Implementation of post-quantum key encapsulation mechanism using Kyber algorithm for secure communication.',
    language: 'Rust',
    framework: 'Actix',
    difficulty: 'Advanced',
    stars: 67,
    image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 6,
    title: 'Distributed Key Management',
    description: 'Secure key management system with air-gapped storage and automated rotation for enterprise applications.',
    language: 'Java',
    framework: 'Spring Boot',
    difficulty: 'Expert',
    stars: 89,
    image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  }
];

const languages = [
  { name: 'All', count: 42 },
  { name: 'JavaScript', count: 12 },
  { name: 'Python', count: 8 },
  { name: 'TypeScript', count: 7 },
  { name: 'Go', count: 6 },
  { name: 'Rust', count: 4 },
  { name: 'Java', count: 5 }
];

const difficulties = [
  { name: 'All', color: 'bg-gray-500' },
  { name: 'Beginner', color: 'bg-green-500' },
  { name: 'Intermediate', color: 'bg-yellow-500' },
  { name: 'Advanced', color: 'bg-orange-500' },
  { name: 'Expert', color: 'bg-red-500' }
];

export default function ExamplesPage() {
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
                Code Examples
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                Real-world code examples and sample applications to help you accelerate 
                your development with ReliQuary's advanced cryptographic features.
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="py-8 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="container-custom">
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <div className="flex-grow">
              <input
                type="text"
                placeholder="Search examples..."
                className="block w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center space-x-2">
              <LightBulbIcon className="h-5 w-5 text-gray-400" />
              <span className="text-gray-600 dark:text-gray-400">Filter:</span>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Language</h4>
              <div className="flex flex-wrap gap-2">
                {languages.map((language) => (
                  <button
                    key={language.name}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      language.name === 'All'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    }`}
                  >
                    {language.name} ({language.count})
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Difficulty</h4>
              <div className="flex flex-wrap gap-2">
                {difficulties.map((difficulty) => (
                  <button
                    key={difficulty.name}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      difficulty.name === 'All'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    }`}
                  >
                    <span className={`inline-block w-2 h-2 rounded-full ${difficulty.color} mr-2`}></span>
                    {difficulty.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Examples */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {examples.map((example, index) => (
              <motion.div
                key={example.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="h-48 overflow-hidden">
                  <img 
                    src={example.image} 
                    alt={example.title} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/50 text-primary-800 dark:text-primary-200">
                      {example.language}
                    </span>
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <StarIcon className="h-4 w-4 text-yellow-400 mr-1" />
                      {example.stars}
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    {example.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {example.description}
                  </p>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {example.framework}
                    </span>
                    <div className="flex items-center">
                      {difficulties.map((difficulty) => (
                        difficulty.name === example.difficulty && (
                          <span 
                            key={difficulty.name} 
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white ${difficulty.color}`}
                          >
                            {example.difficulty}
                          </span>
                        )
                      ))}
                    </div>
                  </div>
                  <div className="flex space-x-3">
                    <Link 
                      href={`/examples/${example.id}`}
                      className="flex-1 btn-primary flex items-center justify-center"
                    >
                      <CodeBracketIcon className="h-5 w-5 mr-2" />
                      View Code
                    </Link>
                    <button className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center justify-center">
                      <CommandLineIcon className="h-5 w-5 mr-2" />
                      Run
                    </button>
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
                3
              </button>
              <span className="px-2 py-2 text-gray-500 dark:text-gray-400">
                ...
              </span>
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                14
              </button>
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                Next
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* GitHub Integration */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex p-3 rounded-lg bg-primary-500 text-white mb-6">
              <CommandLineIcon className="h-8 w-8" />
            </div>
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Clone Our Examples Repository
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
              All our code examples are available in our GitHub repository with detailed 
              documentation and setup instructions.
            </p>
            
            <div className="bg-gray-900 rounded-2xl p-6 max-w-2xl mx-auto mb-8">
              <div className="flex items-center justify-between mb-4">
                <div className="flex space-x-2">
                  <div className="h-3 w-3 rounded-full bg-red-500"></div>
                  <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
                  <div className="h-3 w-3 rounded-full bg-green-500"></div>
                </div>
                <span className="text-gray-400 text-sm">terminal</span>
              </div>
              <pre className="text-green-400 text-left">
                <code>git clone https://github.com/reliquary/reliquary-examples.git
cd reliquary-examples
npm install
npm start</code>
              </pre>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a 
                href="https://github.com/reliquary/reliquary-examples" 
                className="btn-primary inline-flex items-center"
              >
                <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
                View on GitHub
              </a>
              <Link 
                href="/docs" 
                className="btn-secondary inline-flex items-center"
              >
                <DocumentTextIcon className="h-5 w-5 mr-2" />
                Documentation
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Contribute */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Contribute Your Examples
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
              Have a great example to share? We welcome contributions from the community 
              to help others learn and build with ReliQuary.
            </p>
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[
                  {
                    title: 'Fork the Repository',
                    description: 'Create your own copy of the examples repository'
                  },
                  {
                    title: 'Add Your Example',
                    description: 'Create a new directory with your code and documentation'
                  },
                  {
                    title: 'Submit a Pull Request',
                    description: 'Share your example with the community'
                  }
                ].map((step, index) => (
                  <div key={index} className="text-center">
                    <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-primary-500 text-white font-bold text-lg mb-4">
                      {index + 1}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {step.description}
                    </p>
                  </div>
                ))}
              </div>
              
              <Link 
                href="/community" 
                className="btn-outline inline-flex items-center"
              >
                Join Our Community
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}