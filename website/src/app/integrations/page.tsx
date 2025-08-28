'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  ArrowsRightLeftIcon, 
  CloudIcon, 
  BuildingOfficeIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const integrations = [
  {
    id: 1,
    name: 'AWS Integration',
    description: 'Seamlessly integrate ReliQuary with Amazon Web Services for secure cloud operations.',
    category: 'Cloud',
    status: 'Stable',
    logo: 'https://images.unsplash.com/photo-1494972308805-463bc619d34e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    features: [
      'Key management in AWS KMS',
      'Secure S3 bucket encryption',
      'Lambda function integration',
      'CloudWatch monitoring'
    ]
  },
  {
    id: 2,
    name: 'Microsoft Azure',
    description: 'Native integration with Microsoft Azure for enterprise-grade security and compliance.',
    category: 'Cloud',
    status: 'Stable',
    logo: 'https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    features: [
      'Azure Key Vault integration',
      'Secure App Service deployment',
      'Active Directory authentication',
      'Compliance reporting'
    ]
  },
  {
    id: 3,
    name: 'Google Cloud',
    description: 'Full integration with Google Cloud Platform for secure, scalable applications.',
    category: 'Cloud',
    status: 'Stable',
    logo: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    features: [
      'Cloud KMS integration',
      'Secure GKE deployments',
      'Identity and Access Management',
      'Audit logging'
    ]
  },
  {
    id: 4,
    name: 'Salesforce',
    description: 'Protect customer data in Salesforce with end-to-end encryption and zero-knowledge proofs.',
    category: 'CRM',
    status: 'Stable',
    logo: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    features: [
      'Customer data encryption',
      'Secure API integration',
      'Compliance automation',
      'Audit trail protection'
    ]
  },
  {
    id: 5,
    name: 'Slack',
    description: 'Secure team communication with encrypted messaging and access controls.',
    category: 'Communication',
    status: 'Stable',
    logo: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    features: [
      'Encrypted message archiving',
      'Access control policies',
      'Compliance monitoring',
      'Integration with workflows'
    ]
  },
  {
    id: 6,
    name: 'GitHub',
    description: 'Secure your code repositories with cryptographic signing and access management.',
    category: 'Development',
    status: 'Stable',
    logo: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    features: [
      'Commit signature verification',
      'Secure CI/CD pipelines',
      'Access control management',
      'Audit logging'
    ]
  }
];

const categories = [
  { name: 'All', count: 24 },
  { name: 'Cloud', count: 8 },
  { name: 'CRM', count: 4 },
  { name: 'Communication', count: 3 },
  { name: 'Development', count: 5 },
  { name: 'Security', count: 4 }
];

export default function IntegrationsPage() {
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
                Platform Integrations
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                Connect ReliQuary with your existing tools and infrastructure for seamless 
                security integration across your technology stack.
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

      {/* Integrations */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {integrations.map((integration, index) => (
              <motion.div
                key={integration.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      <img 
                        src={integration.logo} 
                        alt={integration.name} 
                        className="h-12 w-12 rounded-lg object-cover mr-4"
                      />
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                          {integration.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {integration.category}
                        </p>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      integration.status === 'Stable' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' 
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'
                    }`}>
                      {integration.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    {integration.description}
                  </p>
                  
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                      Key Features
                    </h4>
                    <ul className="space-y-2">
                      {integration.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-start">
                          <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700 dark:text-gray-300 text-sm">
                            {feature}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex space-x-3">
                    <Link 
                      href={`/integrations/${integration.id}`}
                      className="flex-1 btn-primary flex items-center justify-center"
                    >
                      <ArrowsRightLeftIcon className="h-5 w-5 mr-2" />
                      Configure
                    </Link>
                    <button className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center justify-center">
                      <CloudIcon className="h-5 w-5 mr-2" />
                      Docs
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Custom Integration */}
          <div className="mt-16 bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl p-8 text-white">
            <div className="max-w-4xl mx-auto">
              <div className="flex flex-col md:flex-row items-center">
                <div className="md:w-2/3 mb-6 md:mb-0 md:pr-8">
                  <h2 className="text-3xl font-bold mb-4">
                    Need a Custom Integration?
                  </h2>
                  <p className="text-xl text-primary-100 mb-6">
                    Our team can build custom integrations for any platform or service 
                    that isn't listed here.
                  </p>
                  <Link 
                    href="/contact" 
                    className="btn-primary bg-white text-primary-600 hover:bg-gray-100 inline-flex items-center"
                  >
                    Request Custom Integration
                    <ArrowRightIcon className="ml-2 h-5 w-5" />
                  </Link>
                </div>
                <div className="md:w-1/3 flex justify-center">
                  <div className="bg-white/20 rounded-full p-6">
                    <BuildingOfficeIcon className="h-16 w-16 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* API Integration */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              RESTful API Integration
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-10">
              Integrate with any platform using our comprehensive RESTful API with full 
              documentation and SDKs.
            </p>
            
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 mb-10 border border-gray-200 dark:border-gray-700">
              <div className="flex flex-col md:flex-row gap-8">
                <div className="md:w-1/2">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                    API Endpoints
                  </h3>
                  <ul className="space-y-3">
                    {[
                      'Authentication & Authorization',
                      'Key Management',
                      'Encryption/Decryption',
                      'Digital Signatures',
                      'Zero-Knowledge Proofs',
                      'Audit Logging'
                    ].map((endpoint, index) => (
                      <li key={index} className="flex items-center">
                        <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center mr-3">
                          <div className="h-2 w-2 rounded-full bg-primary-500"></div>
                        </div>
                        <span className="text-gray-700 dark:text-gray-300">{endpoint}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="md:w-1/2">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                    Supported Protocols
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      'OAuth 2.0', 'JWT', 'OpenID Connect',
                      'SAML', 'LDAP', 'SCIM'
                    ].map((protocol, index) => (
                      <div 
                        key={index} 
                        className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center"
                      >
                        <span className="font-medium text-gray-900 dark:text-white">
                          {protocol}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link 
                href="/api-reference" 
                className="btn-primary inline-flex items-center"
              >
                <ArrowsRightLeftIcon className="h-5 w-5 mr-2" />
                API Documentation
              </Link>
              <Link 
                href="/docs" 
                className="btn-secondary inline-flex items-center"
              >
                <CloudIcon className="h-5 w-5 mr-2" />
                Integration Guides
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Enterprise Integration */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
                Enterprise Integration
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400">
                Specialized solutions for large organizations with complex integration requirements.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  title: 'Single Sign-On (SSO)',
                  description: 'Integrate with your existing identity providers for seamless authentication.',
                  icon: BuildingOfficeIcon
                },
                {
                  title: 'Compliance Automation',
                  description: 'Automatically generate compliance reports for SOC 2, HIPAA, GDPR, and more.',
                  icon: CheckCircleIcon
                },
                {
                  title: 'Custom Connectors',
                  description: 'Build custom connectors for proprietary systems and legacy applications.',
                  icon: ArrowsRightLeftIcon
                }
              ].map((service, index) => (
                <div 
                  key={index} 
                  className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 text-center"
                >
                  <div className="inline-flex p-3 rounded-lg bg-primary-500 text-white mb-4">
                    <service.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {service.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {service.description}
                  </p>
                  <Link 
                    href="/enterprise" 
                    className="text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300 transition-colors flex items-center justify-center"
                  >
                    Learn more
                    <ArrowRightIcon className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}