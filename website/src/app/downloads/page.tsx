'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowDownTrayIcon,
  CommandLineIcon,
  CubeIcon,
  DocumentTextIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  PlayIcon,
  ServerIcon,
  CloudIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';

const packages = [
  {
    name: 'Python SDK',
    description: 'Full-featured Python client library with async support',
    version: 'v5.0.0',
    size: '2.3 MB',
    downloads: '15.2K',
    icon: '🐍',
    color: 'blue',
    repository: 'PyPI',
    install: 'pip install reliquary-sdk',
    links: {
      pypi: 'https://pypi.org/project/reliquary-sdk/',
      docs: '/docs/python',
      examples: 'https://github.com/reliquary/examples/python'
    },
    features: [
      'Full API coverage',
      'Async/await support',
      'Type hints included',
      'Comprehensive error handling',
      'Built-in retry logic',
      'Context management'
    ]
  },
  {
    name: 'JavaScript/Node.js SDK',
    description: 'Modern JavaScript SDK with TypeScript definitions',
    version: 'v5.0.0',
    size: '1.8 MB',
    downloads: '12.7K',
    icon: '📦',
    color: 'yellow',
    repository: 'npm',
    install: 'npm install @reliquary/sdk',
    links: {
      npm: 'https://npmjs.com/package/@reliquary/sdk',
      docs: '/docs/javascript',
      examples: 'https://github.com/reliquary/examples/javascript'
    },
    features: [
      'ES6+ modules',
      'TypeScript definitions',
      'Promise-based API',
      'Browser compatibility',
      'Webpack ready',
      'Tree-shakeable'
    ]
  },
  {
    name: 'Java SDK',
    description: 'Enterprise Java client with Spring Boot integration',
    version: 'v5.0.0',
    size: '3.1 MB',
    downloads: '8.9K',
    icon: '☕',
    color: 'orange',
    repository: 'Maven Central',
    install: 'implementation "io.reliquary:sdk:5.0.0"',
    links: {
      maven: 'https://central.sonatype.com/artifact/io.reliquary/sdk',
      docs: '/docs/java',
      examples: 'https://github.com/reliquary/examples/java'
    },
    features: [
      'Spring Boot starter',
      'Reactive support',
      'Connection pooling',
      'Metrics integration',
      'Health checks',
      'Auto-configuration'
    ]
  },
  {
    name: 'Go SDK',
    description: 'Lightweight Go client with concurrent support',
    version: 'v5.0.0',
    size: '1.2 MB',
    downloads: '6.5K',
    icon: '🐹',
    color: 'cyan',
    repository: 'Go Modules',
    install: 'go get github.com/reliquary/go-sdk',
    links: {
      github: 'https://github.com/reliquary/go-sdk',
      docs: '/docs/go',
      examples: 'https://github.com/reliquary/examples/go'
    },
    features: [
      'Zero dependencies',
      'Goroutine safe',
      'Context support',
      'HTTP/2 ready',
      'Memory efficient',
      'Fast JSON parsing'
    ]
  }
];

const deploymentOptions = [
  {
    name: 'Docker Containers',
    description: 'Pre-built Docker images for quick deployment',
    icon: CubeIcon,
    color: 'blue',
    commands: [
      '# Pull the latest image',
      'docker pull reliquary/platform:latest',
      '',
      '# Run with docker-compose',
      'curl -O https://install.reliquary.io/docker-compose.yml',
      'docker-compose up -d'
    ],
    links: [
      { label: 'Docker Hub', url: 'https://hub.docker.com/r/reliquary/platform' },
      { label: 'Docker Guide', url: '/docs/docker' }
    ]
  },
  {
    name: 'Kubernetes Helm',
    description: 'Production-ready Kubernetes deployment with Helm',
    icon: ServerIcon,
    color: 'purple',
    commands: [
      '# Add Helm repository',
      'helm repo add reliquary https://charts.reliquary.io',
      'helm repo update',
      '',
      '# Install ReliQuary',
      'helm install reliquary reliquary/platform \\',
      '  --set config.apiKey=your_api_key'
    ],
    links: [
      { label: 'Helm Charts', url: 'https://github.com/reliquary/helm-charts' },
      { label: 'K8s Guide', url: '/docs/kubernetes' }
    ]
  },
  {
    name: 'Cloud Marketplaces',
    description: 'One-click deployment from cloud marketplaces',
    icon: CloudIcon,
    color: 'green',
    commands: [
      '# AWS Marketplace',
      'aws marketplace subscribe --product-id reliquary-enterprise',
      '',
      '# Azure Marketplace',
      'az vm create --image reliquary:enterprise:latest',
      '',
      '# GCP Marketplace',
      'gcloud deployment-manager deployments create reliquary'
    ],
    links: [
      { label: 'AWS Marketplace', url: 'https://aws.amazon.com/marketplace/reliquary' },
      { label: 'Azure Marketplace', url: 'https://azuremarketplace.microsoft.com/reliquary' }
    ]
  },
  {
    name: 'One-Click Installers',
    description: 'Automated installation scripts for all platforms',
    icon: ComputerDesktopIcon,
    color: 'orange',
    commands: [
      '# Linux/macOS',
      'curl -sSL https://install.reliquary.io | bash',
      '',
      '# Windows PowerShell',
      'iwr -useb https://install.reliquary.io/windows.ps1 | iex',
      '',
      '# Verify installation',
      'reliquary --version'
    ],
    links: [
      { label: 'Installation Guide', url: '/docs/installation' },
      { label: 'System Requirements', url: '/docs/requirements' }
    ]
  }
];

const quickStartSteps = [
  {
    step: 1,
    title: 'Get API Key',
    description: 'Sign up and get your free API key',
    action: 'Sign Up Free',
    link: '/signup'
  },
  {
    step: 2,
    title: 'Install SDK',
    description: 'Choose your preferred language and install',
    action: 'View SDKs',
    link: '#sdks'
  },
  {
    step: 3,
    title: 'Start Building',
    description: 'Follow our quick start guide',
    action: 'Quick Start',
    link: '/docs/quickstart'
  }
];

export default function Downloads() {
  const [activeDeployment, setActiveDeployment] = useState(0);
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  const copyCommand = async (command: string) => {
    try {
      await navigator.clipboard.writeText(command);
      setCopiedCommand(command);
      setTimeout(() => setCopiedCommand(null), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container-custom py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="heading-lg text-gray-900 mb-6">
              Download & Install ReliQuary
            </h1>
            <p className="text-large text-gray-600 mb-8">
              Get started with ReliQuary in minutes. Choose from our SDKs, deployment options, 
              or one-click installers for your preferred platform.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="#sdks" className="btn-primary">
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                Download SDKs
              </a>
              <a href="#deployment" className="btn-outline">
                <ServerIcon className="h-5 w-5 mr-2" />
                Deploy Now
              </a>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Quick Start Steps */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h2 className="heading-md text-gray-900 mb-6">
              Get Started in 3 Steps
            </h2>
            <p className="text-large text-gray-600">
              From zero to production in minutes with our streamlined onboarding process.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {quickStartSteps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-full font-bold text-xl mb-4">
                  {step.step}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {step.description}
                </p>
                <a
                  href={step.link}
                  className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium"
                >
                  {step.action}
                  <PlayIcon className="h-4 w-4 ml-1" />
                </a>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SDKs Section */}
      <section id="sdks" className="section-padding">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h2 className="heading-md text-gray-900 mb-6">
              Official SDKs & Libraries
            </h2>
            <p className="text-large text-gray-600">
              Native SDKs for popular programming languages with comprehensive documentation and examples.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            {packages.map((pkg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-xl transition-all duration-300"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="text-3xl">{pkg.icon}</div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        {pkg.name}
                      </h3>
                      <p className="text-gray-600">{pkg.description}</p>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    pkg.color === 'blue' ? 'bg-blue-100 text-blue-700' :
                    pkg.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                    pkg.color === 'orange' ? 'bg-orange-100 text-orange-700' :
                    'bg-cyan-100 text-cyan-700'
                  }`}>
                    {pkg.version}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Size:</span> {pkg.size}
                  </div>
                  <div>
                    <span className="font-medium">Downloads:</span> {pkg.downloads}
                  </div>
                  <div>
                    <span className="font-medium">Registry:</span> {pkg.repository}
                  </div>
                </div>

                {/* Installation Command */}
                <div className="bg-gray-900 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">Installation</span>
                    <button
                      onClick={() => copyCommand(pkg.install)}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {copiedCommand === pkg.install ? (
                        <CheckIcon className="h-4 w-4" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  <code className="text-green-400 text-sm">
                    {pkg.install}
                  </code>
                </div>

                {/* Features */}
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Key Features:</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {pkg.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center space-x-2">
                        <CheckIcon className="h-4 w-4 text-green-500" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Links */}
                <div className="flex flex-wrap gap-3">
                  {Object.entries(pkg.links).map(([type, url]) => (
                    <a
                      key={type}
                      href={url}
                      target={url.startsWith('http') ? '_blank' : '_self'}
                      rel={url.startsWith('http') ? 'noopener noreferrer' : ''}
                      className="inline-flex items-center px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors capitalize"
                    >
                      {type === 'pypi' ? 'PyPI' : 
                       type === 'npm' ? 'NPM' :
                       type === 'maven' ? 'Maven' :
                       type}
                    </a>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Deployment Options */}
      <section id="deployment" className="section-padding bg-white">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h2 className="heading-md text-gray-900 mb-6">
              Deployment Options
            </h2>
            <p className="text-large text-gray-600">
              Choose from multiple deployment methods to fit your infrastructure and requirements.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-4 gap-4 mb-8">
            {deploymentOptions.map((option, index) => (
              <button
                key={index}
                onClick={() => setActiveDeployment(index)}
                className={`text-left p-4 rounded-lg transition-all ${
                  activeDeployment === index
                    ? 'bg-primary-50 border-2 border-primary-200'
                    : 'bg-gray-50 border-2 border-transparent hover:border-gray-200'
                }`}
              >
                <div className={`inline-flex p-2 rounded-lg mb-3 ${
                  option.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                  option.color === 'purple' ? 'bg-purple-100 text-purple-600' :
                  option.color === 'green' ? 'bg-green-100 text-green-600' :
                  'bg-orange-100 text-orange-600'
                }`}>
                  <option.icon className="h-6 w-6" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  {option.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {option.description}
                </p>
              </button>
            ))}
          </div>

          {/* Deployment Details */}
          <motion.div
            key={activeDeployment}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-white border border-gray-200 rounded-lg p-8"
          >
            <div className="grid lg:grid-cols-2 gap-8">
              <div>
                <div className="flex items-center space-x-3 mb-6">
                  <deploymentOptions[activeDeployment].icon className={`h-8 w-8 ${
                    deploymentOptions[activeDeployment].color === 'blue' ? 'text-blue-600' :
                    deploymentOptions[activeDeployment].color === 'purple' ? 'text-purple-600' :
                    deploymentOptions[activeDeployment].color === 'green' ? 'text-green-600' :
                    'text-orange-600'
                  }`} />
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">
                      {deploymentOptions[activeDeployment].name}
                    </h3>
                    <p className="text-gray-600">
                      {deploymentOptions[activeDeployment].description}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  {deploymentOptions[activeDeployment].links.map((link, linkIndex) => (
                    <a
                      key={linkIndex}
                      href={link.url}
                      target={link.url.startsWith('http') ? '_blank' : '_self'}
                      rel={link.url.startsWith('http') ? 'noopener noreferrer' : ''}
                      className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium mr-6"
                    >
                      <DocumentTextIcon className="h-4 w-4 mr-1" />
                      {link.label}
                    </a>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Installation Commands</h4>
                <div className="bg-gray-900 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-gray-400 text-sm ml-4">Terminal</span>
                  </div>
                  <pre className="text-green-400 text-sm overflow-x-auto">
                    <code>{deploymentOptions[activeDeployment].commands.join('\n')}</code>
                  </pre>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* System Requirements */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="heading-md text-gray-900 mb-8 text-center">
              System Requirements
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Minimum Requirements
                </h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>CPU: 2 cores, 2.0 GHz</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>Memory: 4 GB RAM</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>Storage: 10 GB available space</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>Network: Outbound HTTPS (443)</span>
                  </li>
                </ul>
              </div>

              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Recommended for Production
                </h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>CPU: 4+ cores, 3.0+ GHz</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>Memory: 16+ GB RAM</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>Storage: 100+ GB SSD</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4 text-green-500" />
                    <span>Network: Load balancer ready</span>
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Support & Help */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h2 className="heading-md text-gray-900 mb-6">
              Need Help Getting Started?
            </h2>
            <p className="text-large text-gray-600 mb-8">
              Our team is here to help you get up and running quickly with comprehensive 
              documentation and support resources.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="/docs" className="btn-primary">
                <DocumentTextIcon className="h-5 w-5 mr-2" />
                View Documentation
              </a>
              <a href="/support" className="btn-outline">
                <CommandLineIcon className="h-5 w-5 mr-2" />
                Get Support
              </a>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}