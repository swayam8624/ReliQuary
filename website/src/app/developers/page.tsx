'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  CodeBracketIcon, 
  DocumentTextIcon, 
  CommandLineIcon,
  AcademicCapIcon,
  LightBulbIcon,
  ArrowRightIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

const developerResources = [
  {
    title: 'Documentation',
    description: 'Comprehensive guides and API references to help you integrate ReliQuary into your applications.',
    icon: DocumentTextIcon,
    href: '/docs',
    color: 'bg-blue-500'
  },
  {
    title: 'API Reference',
    description: 'Detailed documentation for all our RESTful and GraphQL APIs with interactive examples.',
    icon: CodeBracketIcon,
    href: '/api-reference',
    color: 'bg-green-500'
  },
  {
    title: 'SDKs & Libraries',
    description: 'Official software development kits for popular programming languages and frameworks.',
    icon: CommandLineIcon,
    href: '/sdks',
    color: 'bg-purple-500'
  },
  {
    title: 'Tutorials',
    description: 'Step-by-step guides and tutorials to help you get started quickly.',
    icon: AcademicCapIcon,
    href: '/tutorials',
    color: 'bg-yellow-500'
  },
  {
    title: 'Code Examples',
    description: 'Real-world code examples and sample applications to accelerate your development.',
    icon: LightBulbIcon,
    href: '/examples',
    color: 'bg-red-500'
  },
  {
    title: 'Community',
    description: 'Connect with other developers, ask questions, and share your experiences.',
    icon: ChatBubbleLeftRightIcon,
    href: '/community',
    color: 'bg-indigo-500'
  }
];

const quickStartSteps = [
  {
    title: 'Sign up for an account',
    description: 'Create your ReliQuary account and get your API keys',
    code: 'npm install @reliquary/sdk'
  },
  {
    title: 'Install the SDK',
    description: 'Add our SDK to your project with your preferred package manager',
    code: 'yarn add @reliquary/sdk'
  },
  {
    title: 'Initialize the client',
    description: 'Configure the SDK with your API keys',
    code: `import { ReliQuaryClient } from '@reliquary/sdk';

const client = new ReliQuaryClient({
  apiKey: 'your-api-key',
  projectId: 'your-project-id'
});`
  },
  {
    title: 'Start building',
    description: 'Use our APIs to integrate cryptographic features into your application',
    code: `// Generate a new key pair
const keyPair = await client.crypto.generateKeyPair();

// Encrypt data
const encrypted = await client.crypto.encrypt(data, publicKey);

// Sign a document
const signature = await client.crypto.sign(document, privateKey);`
  }
];

export default function DevelopersPage() {
  const [activeStep, setActiveStep] = useState(0);

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
                Developer Resources
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                Everything you need to build secure, scalable applications with ReliQuary's 
                enterprise-grade cryptographic platform.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link 
                  href="/signup" 
                  className="btn-primary inline-flex items-center"
                >
                  Get Started
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </Link>
                <Link 
                  href="/docs" 
                  className="btn-secondary inline-flex items-center"
                >
                  <BookOpenIcon className="mr-2 h-5 w-5" />
                  Read Documentation
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Quick Start Guide */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Quick Start Guide
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Get up and running with ReliQuary in minutes with our simple integration process.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="space-y-8">
                {quickStartSteps.map((step, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className={`p-6 rounded-xl cursor-pointer transition-all duration-300 ${
                      activeStep === index 
                        ? 'bg-primary-50 dark:bg-primary-900/20 border-l-4 border-primary-500' 
                        : 'bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                    onClick={() => setActiveStep(index)}
                  >
                    <div className="flex items-start">
                      <div className={`flex-shrink-0 h-10 w-10 rounded-full ${step.color} flex items-center justify-center text-white mr-4`}>
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                          {step.title}
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                          {step.description}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            <motion.div
              key={activeStep}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-gray-900 rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-400 text-sm">example.js</span>
                <div className="flex space-x-2">
                  <div className="h-3 w-3 rounded-full bg-red-500"></div>
                  <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
                  <div className="h-3 w-3 rounded-full bg-green-500"></div>
                </div>
              </div>
              <pre className="text-green-400 text-sm overflow-x-auto">
                <code>{quickStartSteps[activeStep].code}</code>
              </pre>
              <div className="mt-4 text-gray-400 text-sm">
                <p>Run this code to get started with ReliQuary</p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Developer Resources */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Developer Resources
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Explore our comprehensive collection of resources to help you build with ReliQuary.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {developerResources.map((resource, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className={`inline-flex p-3 rounded-lg ${resource.color} text-white mb-4`}>
                  <resource.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {resource.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {resource.description}
                </p>
                <Link 
                  href={resource.href}
                  className="text-primary-600 dark:text-primary-400 font-medium flex items-center hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                >
                  Learn more
                  <ArrowRightIcon className="ml-1 h-4 w-4" />
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Support Section */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              Need Help?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-10">
              Our developer support team is here to help you succeed with ReliQuary.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="p-6 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <DocumentTextIcon className="h-10 w-10 text-primary-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Documentation
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Comprehensive guides and API references
                </p>
                <Link 
                  href="/docs" 
                  className="text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300"
                >
                  Browse Docs
                </Link>
              </div>
              
              <div className="p-6 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <ChatBubbleLeftRightIcon className="h-10 w-10 text-primary-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Community
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Connect with other developers and get help
                </p>
                <Link 
                  href="/community" 
                  className="text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300"
                >
                  Join Community
                </Link>
              </div>
              
              <div className="p-6 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <CommandLineIcon className="h-10 w-10 text-primary-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Support
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Get professional support for your projects
                </p>
                <Link 
                  href="/support" 
                  className="text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300"
                >
                  Contact Support
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}