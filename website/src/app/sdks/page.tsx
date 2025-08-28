'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  CommandLineIcon, 
  ArrowDownTrayIcon, 
  DocumentTextIcon,
  LightBulbIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const sdks = [
  {
    id: 1,
    name: 'JavaScript SDK',
    description: 'Official SDK for Node.js and browser environments with full TypeScript support.',
    language: 'JavaScript',
    version: 'v2.4.1',
    downloads: '12,458',
    lastUpdated: '2024-05-15',
    status: 'Stable',
    github: 'https://github.com/reliquary/reliquary-js',
    documentation: '/docs/javascript-sdk',
    features: [
      'Full TypeScript support',
      'Promise-based API',
      'Automatic retries',
      'Request/response logging',
      'Webhook handling'
    ]
  },
  {
    id: 2,
    name: 'Python SDK',
    description: 'Comprehensive Python library for integrating ReliQuary into your Python applications.',
    language: 'Python',
    version: 'v1.8.3',
    downloads: '8,742',
    lastUpdated: '2024-05-10',
    status: 'Stable',
    github: 'https://github.com/reliquary/reliquary-python',
    documentation: '/docs/python-sdk',
    features: [
      'Synchronous and asynchronous support',
      'Type hints for all functions',
      'Built-in retry logic',
      'Webhook signature verification',
      'CLI tools included'
    ]
  },
  {
    id: 3,
    name: 'Go SDK',
    description: 'High-performance Go library with minimal dependencies for maximum efficiency.',
    language: 'Go',
    version: 'v1.2.7',
    downloads: '5,321',
    lastUpdated: '2024-05-08',
    status: 'Stable',
    github: 'https://github.com/reliquary/reliquary-go',
    documentation: '/docs/go-sdk',
    features: [
      'Context-aware requests',
      'Built-in connection pooling',
      'Structured logging',
      'Request tracing support',
      'Modular design'
    ]
  },
  {
    id: 4,
    name: 'Java SDK',
    description: 'Enterprise-grade Java library with Spring Boot integration and comprehensive testing.',
    language: 'Java',
    version: 'v3.1.0',
    downloads: '6,894',
    lastUpdated: '2024-05-12',
    status: 'Stable',
    github: 'https://github.com/reliquary/reliquary-java',
    documentation: '/docs/java-sdk',
    features: [
      'Spring Boot auto-configuration',
      'Fluent API design',
      'Comprehensive exception handling',
      'Webhook validation',
      'Javadoc for all classes'
    ]
  },
  {
    id: 5,
    name: 'Rust SDK',
    description: 'Memory-safe Rust library with zero-cost abstractions and excellent performance.',
    language: 'Rust',
    version: 'v0.9.4',
    downloads: '2,156',
    lastUpdated: '2024-05-05',
    status: 'Beta',
    github: 'https://github.com/reliquary/reliquary-rust',
    documentation: '/docs/rust-sdk',
    features: [
      'Zero-copy deserialization',
      'Async/await support',
      'Compile-time guarantees',
      'WebAssembly compatible',
      'Extensive test coverage'
    ]
  },
  {
    id: 6,
    name: 'React Components',
    description: 'Pre-built React components for common ReliQuary UI patterns and workflows.',
    language: 'TypeScript',
    version: 'v1.5.2',
    downloads: '4,673',
    lastUpdated: '2024-05-14',
    status: 'Stable',
    github: 'https://github.com/reliquary/reliquary-react',
    documentation: '/docs/react-components',
    features: [
      'Dark mode support',
      'Accessible components',
      'Customizable themes',
      'TypeScript definitions',
      'Tree-shakeable imports'
    ]
  }
];

const languages = [
  { name: 'All', count: 18 },
  { name: 'JavaScript', count: 3 },
  { name: 'Python', count: 2 },
  { name: 'Go', count: 1 },
  { name: 'Java', count: 2 },
  { name: 'Rust', count: 1 },
  { name: 'TypeScript', count: 4 }
];

export default function SDKsPage() {
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
                Software Development Kits
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                Official SDKs and libraries for integrating ReliQuary into your applications 
                across multiple programming languages and frameworks.
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Language Filter */}
      <div className="py-8 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="container-custom">
          <div className="flex flex-wrap gap-2">
            {languages.map((language) => (
              <button
                key={language.name}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
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
      </div>

      {/* SDKs */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {sdks.map((sdk, index) => (
              <motion.div
                key={sdk.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                        {sdk.name}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {sdk.description}
                      </p>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        sdk.status === 'Stable' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' 
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'
                      }`}>
                        {sdk.status}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {sdk.version}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 mb-6">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/50 text-primary-800 dark:text-primary-200">
                      {sdk.language}
                    </span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                      {sdk.downloads} downloads
                    </span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                      Updated {sdk.lastUpdated}
                    </span>
                  </div>
                  
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                      Key Features
                    </h4>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {sdk.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-start">
                          <div className="flex-shrink-0 h-5 w-5 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center mr-2 mt-0.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary-500"></div>
                          </div>
                          <span className="text-gray-700 dark:text-gray-300 text-sm">
                            {feature}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex flex-wrap gap-3">
                    <a 
                      href={sdk.github}
                      className="flex-1 btn-primary flex items-center justify-center"
                    >
                      <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                      Download
                    </a>
                    <Link 
                      href={sdk.documentation}
                      className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center justify-center"
                    >
                      <DocumentTextIcon className="h-5 w-5 mr-2" />
                      Docs
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Installation Guide */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
                Quick Installation
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400">
                Get started with any of our SDKs in minutes
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                  <CommandLineIcon className="h-6 w-6 text-primary-500 mr-2" />
                  JavaScript/TypeScript
                </h3>
                <div className="bg-gray-900 rounded-lg p-4 mb-4">
                  <pre className="text-green-400 text-sm">
                    <code>npm install @reliquary/sdk</code>
                  </pre>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Or with yarn: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">yarn add @reliquary/sdk</code>
                </p>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                  <CommandLineIcon className="h-6 w-6 text-primary-500 mr-2" />
                  Python
                </h3>
                <div className="bg-gray-900 rounded-lg p-4 mb-4">
                  <pre className="text-green-400 text-sm">
                    <code>pip install reliquary-sdk</code>
                  </pre>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Or with conda: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">conda install reliquary-sdk</code>
                </p>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                  <CommandLineIcon className="h-6 w-6 text-primary-500 mr-2" />
                  Go
                </h3>
                <div className="bg-gray-900 rounded-lg p-4 mb-4">
                  <pre className="text-green-400 text-sm">
                    <code>go get github.com/reliquary/reliquary-go</code>
                  </pre>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Then import: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">import "github.com/reliquary/reliquary-go"</code>
                </p>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                  <CommandLineIcon className="h-6 w-6 text-primary-500 mr-2" />
                  Java
                </h3>
                <div className="bg-gray-900 rounded-lg p-4 mb-4">
                  <pre className="text-green-400 text-sm">
                    <code>{`<dependency>
  <groupId>io.reliquary</groupId>
  <artifactId>reliquary-sdk</artifactId>
  <version>3.1.0</version>
</dependency>`}</code>
                  </pre>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Add to your Maven pom.xml or Gradle build file
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Community and Support */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex p-3 rounded-lg bg-primary-500 text-white mb-6">
              <LightBulbIcon className="h-8 w-8" />
            </div>
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Need Help or Want to Contribute?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-10">
              Our community and support resources are here to help you succeed with ReliQuary SDKs.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
              {[
                {
                  title: 'Documentation',
                  description: 'Comprehensive guides and API references',
                  icon: DocumentTextIcon,
                  link: '/docs',
                  color: 'bg-blue-500'
                },
                {
                  title: 'GitHub Issues',
                  description: 'Report bugs and request features',
                  icon: CommandLineIcon,
                  link: 'https://github.com/reliquary',
                  color: 'bg-gray-800'
                },
                {
                  title: 'Community Forum',
                  description: 'Connect with other developers',
                  icon: LightBulbIcon,
                  link: '/community',
                  color: 'bg-purple-500'
                }
              ].map((resource, index) => (
                <div 
                  key={index} 
                  className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
                >
                  <div className={`inline-flex p-2 rounded-lg ${resource.color} text-white mb-4`}>
                    <resource.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {resource.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {resource.description}
                  </p>
                  <Link 
                    href={resource.link}
                    className="text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300 transition-colors flex items-center"
                  >
                    Learn more
                    <ArrowRightIcon className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              ))}
            </div>
            
            <div className="bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">
                Stay Updated on SDK Releases
              </h3>
              <p className="text-primary-100 mb-6">
                Subscribe to our developer newsletter for SDK updates, new features, and best practices.
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}