'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  CodeBracketIcon,
  KeyIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  PlayIcon,
  CubeIcon,
  ClipboardDocumentIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

const apiEndpoints = [
  {
    category: 'Authentication',
    icon: KeyIcon,
    color: 'blue',
    endpoints: [
      {
        method: 'POST',
        path: '/auth/login',
        description: 'Authenticate user and get JWT token',
        example: {
          request: {
            email: 'user@example.com',
            password: 'secure_password'
          },
          response: {
            access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            token_type: 'bearer',
            expires_in: 3600
          }
        }
      },
      {
        method: 'POST',
        path: '/auth/register',
        description: 'Register new user account',
        example: {
          request: {
            email: 'user@example.com',
            password: 'secure_password',
            organization: 'ACME Corp'
          },
          response: {
            user_id: 'usr_abc123',
            message: 'User created successfully'
          }
        }
      }
    ]
  },
  {
    category: 'Vault Operations',
    icon: ShieldCheckIcon,
    color: 'green',
    endpoints: [
      {
        method: 'POST',
        path: '/vault/store',
        description: 'Store encrypted data in vault',
        example: {
          request: {
            data: 'sensitive_information',
            encryption_algorithm: 'kyber-1024',
            context_required: true,
            consensus_threshold: 3
          },
          response: {
            vault_id: 'vault_xyz789',
            encryption_key_id: 'key_def456',
            created_at: '2024-01-15T10:30:00Z'
          }
        }
      },
      {
        method: 'GET',
        path: '/vault/{vault_id}',
        description: 'Retrieve encrypted data from vault',
        example: {
          response: {
            vault_id: 'vault_xyz789',
            data: 'decrypted_data',
            consensus_result: 'approved',
            access_granted_at: '2024-01-15T10:35:00Z'
          }
        }
      }
    ]
  },
  {
    category: 'Consensus System',
    icon: CubeIcon,
    color: 'purple',
    endpoints: [
      {
        method: 'POST',
        path: '/consensus/decision',
        description: 'Request multi-agent consensus decision',
        example: {
          request: {
            proposal: 'vault_access_request',
            context: {
              user_id: 'usr_abc123',
              vault_id: 'vault_xyz789',
              location: 'San Francisco, CA'
            },
            threshold: 0.75
          },
          response: {
            decision_id: 'dec_ghi012',
            result: 'approved',
            confidence: 0.85,
            agent_votes: {
              neutral: 'approve',
              strict: 'approve', 
              permissive: 'approve',
              watchdog: 'approve'
            }
          }
        }
      }
    ]
  },
  {
    category: 'Zero-Knowledge Proofs',
    icon: DocumentTextIcon,
    color: 'orange',
    endpoints: [
      {
        method: 'POST',
        path: '/zk/generate-proof',
        description: 'Generate zero-knowledge proof',
        example: {
          request: {
            statement: 'age >= 21',
            private_data: { age: 25 },
            circuit_id: 'age_verification'
          },
          response: {
            proof: '0x1a2b3c...',
            public_signals: ['1'],
            verification_key: 'vk_jkl345'
          }
        }
      },
      {
        method: 'POST',
        path: '/zk/verify-proof',
        description: 'Verify zero-knowledge proof',
        example: {
          request: {
            proof: '0x1a2b3c...',
            public_signals: ['1'],
            verification_key: 'vk_jkl345'
          },
          response: {
            valid: true,
            verified_at: '2024-01-15T10:40:00Z'
          }
        }
      }
    ]
  }
];

const codeExamples = {
  python: `import requests
from reliquary import ReliQuaryClient

# Initialize client
client = ReliQuaryClient(
    api_key="your_api_key",
    base_url="https://api.reliquary.io"
)

# Store sensitive data
result = client.vault.store(
    data="confidential_document",
    encryption_algorithm="kyber-1024",
    context_required=True
)

print(f"Stored with ID: {result.vault_id}")

# Retrieve data with consensus
data = client.vault.retrieve(
    vault_id=result.vault_id,
    context={
        "location": "trusted_location",
        "device_fingerprint": "abc123"
    }
)

print(f"Retrieved: {data}")`,

  javascript: `import { ReliQuaryClient } from '@reliquary/sdk';

// Initialize client
const client = new ReliQuaryClient({
  apiKey: 'your_api_key',
  baseURL: 'https://api.reliquary.io'
});

// Store sensitive data
const result = await client.vault.store({
  data: 'confidential_document',
  encryptionAlgorithm: 'kyber-1024',
  contextRequired: true
});

console.log(\`Stored with ID: \${result.vaultId}\`);

// Retrieve data with consensus
const data = await client.vault.retrieve({
  vaultId: result.vaultId,
  context: {
    location: 'trusted_location',
    deviceFingerprint: 'abc123'
  }
});

console.log('Retrieved:', data);`,

  curl: `# Store data in vault
curl -X POST "https://api.reliquary.io/vault/store" \\
  -H "Authorization: Bearer your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "data": "confidential_document",
    "encryption_algorithm": "kyber-1024",
    "context_required": true
  }'

# Retrieve data from vault
curl -X GET "https://api.reliquary.io/vault/vault_xyz789" \\
  -H "Authorization: Bearer your_api_key" \\
  -H "X-Context: eyJsb2NhdGlvbiI6InRydXN0ZWRfbG9jYXRpb24ifQ=="`
};

export default function ApiDocumentation() {
  const [activeEndpoint, setActiveEndpoint] = useState(0);
  const [activeLanguage, setActiveLanguage] = useState<'python' | 'javascript' | 'curl'>('python');
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(type);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container-custom py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="heading-lg text-gray-900 mb-6">
              ReliQuary API Documentation
            </h1>
            <p className="text-large text-gray-600 mb-8">
              Complete reference for integrating ReliQuary's cryptographic platform 
              with comprehensive examples and interactive tools.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="#get-started"
                className="btn-primary"
              >
                <PlayIcon className="h-5 w-5 mr-2" />
                Get Started
              </a>
              <a
                href="#swagger-ui"
                className="btn-outline"
              >
                <DocumentTextIcon className="h-5 w-5 mr-2" />
                Interactive API
              </a>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Quick Start */}
      <section id="get-started" className="section-padding">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="heading-md text-gray-900 mb-8 text-center">
              Quick Start Guide
            </h2>

            {/* Language Selector */}
            <div className="flex justify-center mb-8">
              <div className="inline-flex bg-gray-100 rounded-lg p-1">
                {Object.keys(codeExamples).map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setActiveLanguage(lang as keyof typeof codeExamples)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all capitalize ${
                      activeLanguage === lang
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {lang === 'javascript' ? 'Node.js' : lang}
                  </button>
                ))}
              </div>
            </div>

            {/* Code Example */}
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 to-purple-500 rounded-lg blur opacity-25"></div>
              <div className="relative bg-gray-900 rounded-lg overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b border-gray-700">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-gray-400 text-sm ml-4">
                      {activeLanguage === 'curl' ? 'Terminal' : `example.${activeLanguage === 'python' ? 'py' : 'js'}`}
                    </span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(codeExamples[activeLanguage], 'code')}
                    className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
                  >
                    {copiedText === 'code' ? (
                      <>
                        <CheckIcon className="h-4 w-4" />
                        <span className="text-sm">Copied!</span>
                      </>
                    ) : (
                      <>
                        <ClipboardDocumentIcon className="h-4 w-4" />
                        <span className="text-sm">Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <div className="p-6">
                  <pre className="text-sm text-green-400 overflow-x-auto">
                    <code>{codeExamples[activeLanguage]}</code>
                  </pre>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* API Endpoints */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h2 className="heading-md text-gray-900 mb-6">
              API Endpoints Reference
            </h2>
            <p className="text-large text-gray-600">
              Explore all available endpoints with real examples and response formats.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            
            {/* Endpoint Categories */}
            <div className="space-y-4">
              {apiEndpoints.map((category, categoryIndex) => (
                <motion.div
                  key={categoryIndex}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: categoryIndex * 0.1 }}
                  className="space-y-2"
                >
                  <div className={`flex items-center space-x-3 p-4 rounded-lg ${
                    category.color === 'blue' ? 'bg-blue-50 text-blue-700' :
                    category.color === 'green' ? 'bg-green-50 text-green-700' :
                    category.color === 'purple' ? 'bg-purple-50 text-purple-700' :
                    'bg-orange-50 text-orange-700'
                  }`}>
                    <category.icon className="h-6 w-6" />
                    <h3 className="font-semibold">{category.category}</h3>
                  </div>
                  
                  {category.endpoints.map((endpoint, endpointIndex) => {
                    const globalIndex = apiEndpoints.slice(0, categoryIndex)
                      .reduce((acc, cat) => acc + cat.endpoints.length, 0) + endpointIndex;
                    
                    return (
                      <button
                        key={endpointIndex}
                        onClick={() => setActiveEndpoint(globalIndex)}
                        className={`w-full text-left p-3 rounded-lg transition-all ${
                          activeEndpoint === globalIndex
                            ? 'bg-primary-50 border-2 border-primary-200'
                            : 'bg-gray-50 border-2 border-transparent hover:border-gray-200'
                        }`}
                      >
                        <div className="flex items-center space-x-2 mb-1">
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${
                            endpoint.method === 'GET' ? 'bg-green-100 text-green-700' :
                            endpoint.method === 'POST' ? 'bg-blue-100 text-blue-700' :
                            endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {endpoint.method}
                          </span>
                          <span className="text-sm font-mono">{endpoint.path}</span>
                        </div>
                        <p className="text-xs text-gray-600">{endpoint.description}</p>
                      </button>
                    );
                  })}
                </motion.div>
              ))}
            </div>

            {/* Endpoint Details */}
            <div className="lg:col-span-2">
              <motion.div
                key={activeEndpoint}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-white border border-gray-200 rounded-lg p-6"
              >
                {(() => {
                  let currentIndex = 0;
                  for (const category of apiEndpoints) {
                    for (const endpoint of category.endpoints) {
                      if (currentIndex === activeEndpoint) {
                        return (
                          <div>
                            <div className="flex items-center space-x-3 mb-4">
                              <span className={`px-3 py-1 text-sm font-semibold rounded ${
                                endpoint.method === 'GET' ? 'bg-green-100 text-green-700' :
                                endpoint.method === 'POST' ? 'bg-blue-100 text-blue-700' :
                                endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {endpoint.method}
                              </span>
                              <code className="text-lg font-mono text-gray-800">
                                {endpoint.path}
                              </code>
                            </div>
                            
                            <p className="text-gray-600 mb-6">{endpoint.description}</p>

                            {/* Request Example */}
                            {endpoint.example.request && (
                              <div className="mb-6">
                                <h4 className="font-semibold text-gray-900 mb-3">Request Example</h4>
                                <div className="bg-gray-900 rounded-lg p-4">
                                  <pre className="text-sm text-green-400 overflow-x-auto">
                                    <code>{JSON.stringify(endpoint.example.request, null, 2)}</code>
                                  </pre>
                                </div>
                              </div>
                            )}

                            {/* Response Example */}
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-3">Response Example</h4>
                              <div className="bg-gray-900 rounded-lg p-4">
                                <pre className="text-sm text-blue-400 overflow-x-auto">
                                  <code>{JSON.stringify(endpoint.example.response, null, 2)}</code>
                                </pre>
                              </div>
                            </div>
                          </div>
                        );
                      }
                      currentIndex++;
                    }
                  }
                  return null;
                })()}
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Swagger UI */}
      <section id="swagger-ui" className="section-padding bg-gray-50">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h2 className="heading-md text-gray-900 mb-6">
              Interactive API Explorer
            </h2>
            <p className="text-large text-gray-600">
              Test endpoints directly from your browser with our interactive Swagger UI.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-white rounded-lg shadow-lg overflow-hidden"
          >
            <div className="bg-gradient-to-r from-primary-500 to-purple-500 text-white p-6">
              <div className="flex items-center space-x-3">
                <CodeBracketIcon className="h-8 w-8" />
                <div>
                  <h3 className="text-xl font-semibold">Swagger UI</h3>
                  <p className="text-primary-100">Try our API endpoints interactively</p>
                </div>
              </div>
            </div>
            
            <div className="p-8 text-center">
              <div className="max-w-md mx-auto">
                <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  Interactive API Documentation
                </h4>
                <p className="text-gray-600 mb-6">
                  Access our full Swagger UI interface to explore and test all API endpoints 
                  with real-time validation and examples.
                </p>
                <a
                  href="https://api.reliquary.io/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary inline-flex items-center"
                >
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Open Swagger UI
                </a>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* API Keys & Authentication */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="heading-md text-gray-900 mb-8 text-center">
              Authentication & API Keys
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card">
                <KeyIcon className="h-8 w-8 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  API Key Authentication
                </h3>
                <p className="text-gray-600 mb-4">
                  Use API keys for server-to-server authentication. Include your API key 
                  in the Authorization header.
                </p>
                <div className="bg-gray-900 rounded-lg p-3">
                  <code className="text-green-400 text-sm">
                    Authorization: Bearer your_api_key_here
                  </code>
                </div>
              </div>

              <div className="card">
                <ShieldCheckIcon className="h-8 w-8 text-green-600 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  OAuth 2.0 / JWT
                </h3>
                <p className="text-gray-600 mb-4">
                  For user-facing applications, use OAuth 2.0 with JWT tokens 
                  for secure authentication.
                </p>
                <div className="bg-gray-900 rounded-lg p-3">
                  <code className="text-blue-400 text-sm">
                    Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
                  </code>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}