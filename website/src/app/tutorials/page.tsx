'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  AcademicCapIcon, 
  CodeBracketIcon, 
  CommandLineIcon,
  LightBulbIcon,
  ArrowRightIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const tutorials = [
  {
    id: 1,
    title: 'Getting Started with ReliQuary SDK',
    description: 'Learn how to install and configure the ReliQuary SDK in your application with step-by-step instructions.',
    duration: '15 min',
    level: 'Beginner',
    category: 'Setup',
    image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 2,
    title: 'Implementing Zero-Knowledge Proofs',
    description: 'A practical guide to implementing zero-knowledge proofs in your applications for enhanced privacy.',
    duration: '25 min',
    level: 'Advanced',
    category: 'Security',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 3,
    title: 'Building Multi-Agent Consensus Systems',
    description: 'Learn how to design and implement distributed consensus systems using autonomous agents.',
    duration: '35 min',
    level: 'Expert',
    category: 'Architecture',
    image: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 4,
    title: 'Post-Quantum Cryptography Migration',
    description: 'Step-by-step guide to migrating your existing cryptographic systems to post-quantum algorithms.',
    duration: '45 min',
    level: 'Advanced',
    category: 'Security',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 5,
    title: 'Threshold Cryptography Implementation',
    description: 'Best practices for implementing threshold cryptography to distribute trust and eliminate single points of failure.',
    duration: '30 min',
    level: 'Advanced',
    category: 'Security',
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 6,
    title: 'Distributed Key Management',
    description: 'Learn how to securely manage cryptographic keys in distributed environments with air-gapped storage.',
    duration: '20 min',
    level: 'Intermediate',
    category: 'Infrastructure',
    image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80'
  }
];

const categories = [
  { name: 'All', count: 36 },
  { name: 'Setup', count: 8 },
  { name: 'Security', count: 14 },
  { name: 'Architecture', count: 6 },
  { name: 'Infrastructure', count: 5 },
  { name: 'Development', count: 3 }
];

const levels = [
  { name: 'Beginner', color: 'bg-green-500' },
  { name: 'Intermediate', color: 'bg-yellow-500' },
  { name: 'Advanced', color: 'bg-orange-500' },
  { name: 'Expert', color: 'bg-red-500' }
];

export default function TutorialsPage() {
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
                Developer Tutorials
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                Step-by-step guides and practical examples to help you master ReliQuary's 
                advanced cryptographic features and build secure applications.
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Categories and Search */}
      <div className="py-8 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="container-custom">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-grow">
              <input
                type="text"
                placeholder="Search tutorials..."
                className="block w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center space-x-2">
              <LightBulbIcon className="h-5 w-5 text-gray-400" />
              <span className="text-gray-600 dark:text-gray-400">Filter:</span>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2 mt-4">
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

      {/* Tutorials */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {tutorials.map((tutorial, index) => (
              <motion.div
                key={tutorial.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="h-48 overflow-hidden">
                  <img 
                    src={tutorial.image} 
                    alt={tutorial.title} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/50 text-primary-800 dark:text-primary-200">
                      {tutorial.category}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {tutorial.duration}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    {tutorial.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {tutorial.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {levels.map((level) => (
                        level.name === tutorial.level && (
                          <span 
                            key={level.name} 
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white ${level.color}`}
                          >
                            {tutorial.level}
                          </span>
                        )
                      ))}
                    </div>
                    <Link 
                      href={`/tutorials/${tutorial.id}`}
                      className="text-primary-600 dark:text-primary-400 font-medium flex items-center hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                    >
                      Start Tutorial
                      <ArrowRightIcon className="ml-1 h-4 w-4" />
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
                3
              </button>
              <span className="px-2 py-2 text-gray-500 dark:text-gray-400">
                ...
              </span>
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                9
              </button>
              <button className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                Next
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* Interactive Learning */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Interactive Learning Experience
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Our tutorials include hands-on exercises, code examples, and real-time feedback 
              to accelerate your learning process.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: 'Hands-On Labs',
                description: 'Interactive coding environments where you can practice what you learn',
                icon: CodeBracketIcon,
                color: 'bg-blue-500'
              },
              {
                title: 'Video Walkthroughs',
                description: 'Step-by-step video guides that demonstrate complex concepts',
                icon: CommandLineIcon,
                color: 'bg-green-500'
              },
              {
                title: 'Community Support',
                description: 'Get help from our developer community and expert mentors',
                icon: AcademicCapIcon,
                color: 'bg-purple-500'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700 text-center"
              >
                <div className={`inline-flex p-3 rounded-lg ${feature.color} text-white mb-4`}>
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Certification */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl p-8 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">
              Earn Your Certification
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Complete our tutorial series and earn a certificate to showcase your expertise 
              in advanced cryptographic security.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold">36</div>
                <div className="text-primary-200">Tutorials</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">12</div>
                <div className="text-primary-200">Hours of Content</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">∞</div>
                <div className="text-primary-200">Career Opportunities</div>
              </div>
            </div>
            
            <Link 
              href="/certification" 
              className="btn-primary bg-white text-primary-600 hover:bg-gray-100 inline-flex items-center"
            >
              Start Learning Path
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}