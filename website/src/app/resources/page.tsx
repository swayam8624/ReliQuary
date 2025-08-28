'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  BookOpenIcon, 
  DocumentTextIcon, 
  NewspaperIcon,
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  LightBulbIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const resourceCategories = [
  {
    title: 'Blog',
    description: 'Insights, tutorials, and industry analysis from our team of experts.',
    icon: NewspaperIcon,
    href: '/blog',
    color: 'bg-blue-500',
    articles: 128
  },
  {
    title: 'Case Studies',
    description: 'Real-world examples of how organizations use ReliQuary to solve complex challenges.',
    icon: DocumentTextIcon,
    href: '/case-studies',
    color: 'bg-green-500',
    articles: 24
  },
  {
    title: 'Whitepapers',
    description: 'In-depth technical research and analysis on cryptographic innovations.',
    icon: BookOpenIcon,
    href: '/whitepapers',
    color: 'bg-purple-500',
    articles: 16
  },
  {
    title: 'Community',
    description: 'Connect with other developers, share knowledge, and participate in discussions.',
    icon: UserGroupIcon,
    href: '/community',
    color: 'bg-yellow-500',
    articles: 1024
  },
  {
    title: 'Support',
    description: 'Documentation, FAQs, and professional support for ReliQuary customers.',
    icon: ChatBubbleLeftRightIcon,
    href: '/support',
    color: 'bg-red-500',
    articles: 86
  },
  {
    title: 'Research',
    description: 'Latest research findings and academic collaborations in cryptography.',
    icon: LightBulbIcon,
    href: '/research',
    color: 'bg-indigo-500',
    articles: 42
  }
];

const featuredResources = [
  {
    title: 'Post-Quantum Cryptography Migration Guide',
    description: 'A comprehensive guide to transitioning your systems to post-quantum cryptographic algorithms.',
    category: 'Whitepaper',
    date: 'May 15, 2024',
    readTime: '12 min read'
  },
  {
    title: 'Building Zero-Knowledge Applications',
    description: 'Learn how to implement zero-knowledge proofs in your applications for enhanced privacy.',
    category: 'Tutorial',
    date: 'April 28, 2024',
    readTime: '8 min read'
  },
  {
    title: 'Enterprise Security Case Study: FinTech Corp',
    description: 'How a leading financial institution implemented ReliQuary to secure their transactions.',
    category: 'Case Study',
    date: 'April 12, 2024',
    readTime: '6 min read'
  },
  {
    title: 'The Future of Distributed Consensus',
    description: 'Exploring new consensus mechanisms for scalable, secure distributed systems.',
    category: 'Research',
    date: 'March 30, 2024',
    readTime: '15 min read'
  }
];

export default function ResourcesPage() {
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
                Knowledge Resources
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                Explore our collection of articles, whitepapers, case studies, and research to 
                stay informed about the latest in cryptographic security and distributed systems.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link 
                  href="/blog" 
                  className="btn-primary inline-flex items-center"
                >
                  Browse All Resources
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Resource Categories */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Resource Categories
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Find exactly what you're looking for with our organized resource categories.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {resourceCategories.map((category, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className={`inline-flex p-3 rounded-lg ${category.color} text-white mb-4`}>
                  <category.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {category.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {category.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {category.articles} articles
                  </span>
                  <Link 
                    href={category.href}
                    className="text-primary-600 dark:text-primary-400 font-medium flex items-center hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                  >
                    Explore
                    <ArrowRightIcon className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Resources */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Featured Resources
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Our most popular and recent resources to help you get started.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {featuredResources.map((resource, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/50 text-primary-800 dark:text-primary-200">
                      {resource.category}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {resource.readTime}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    {resource.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {resource.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {resource.date}
                    </span>
                    <button className="text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300 transition-colors">
                      Read now
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link 
              href="/blog" 
              className="btn-outline inline-flex items-center"
            >
              View All Resources
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
              Stay Updated
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Subscribe to our newsletter for the latest resources, research, and product updates.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-grow px-4 py-3 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent"
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