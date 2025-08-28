// Security and Compliance Documentation Suite
// Comprehensive security documentation and compliance management

'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ShieldCheckIcon,
  DocumentTextIcon,
  LockClosedIcon,
  KeyIcon,
  ServerIcon,
  ClockIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { gdprComplianceManager } from '@/lib/gdpr-compliance';

interface SecurityControl {
  id: string;
  category: string;
  name: string;
  description: string;
  status: 'implemented' | 'planned' | 'in-progress' | 'not-applicable';
  evidence?: string;
  lastAudited?: string;
}

interface ComplianceStandard {
  id: string;
  name: string;
  description: string;
  status: 'compliant' | 'in-progress' | 'not-started';
  controls: SecurityControl[];
  lastAudit?: string;
  nextAudit?: string;
}

interface AuditLog {
  id: string;
  action: string;
  user: string;
  timestamp: string;
  ipAddress: string;
  details: string;
}

const SECURITY_CONTROLS: SecurityControl[] = [
  {
    id: 'sc_001',
    category: 'Data Protection',
    name: 'End-to-End Encryption',
    description: 'All data is encrypted using post-quantum cryptographic algorithms both in transit and at rest',
    status: 'implemented',
    evidence: 'Cryptography audit report Q4 2023',
    lastAudited: '2023-12-15'
  },
  {
    id: 'sc_002',
    category: 'Access Control',
    name: 'Multi-Factor Authentication',
    description: 'MFA required for all administrative and sensitive operations',
    status: 'implemented',
    evidence: 'Authentication system audit',
    lastAudited: '2024-01-10'
  },
  {
    id: 'sc_003',
    category: 'Data Protection',
    name: 'Zero-Knowledge Architecture',
    description: 'Customer data is processed without knowledge of its contents',
    status: 'implemented',
    evidence: 'System architecture documentation',
    lastAudited: '2023-11-20'
  },
  {
    id: 'sc_004',
    category: 'Network Security',
    name: 'DDoS Protection',
    description: 'Enterprise-grade DDoS protection for all services',
    status: 'implemented',
    evidence: 'Cloud provider security report',
    lastAudited: '2024-01-05'
  },
  {
    id: 'sc_005',
    category: 'Incident Response',
    name: '24/7 Security Monitoring',
    description: 'Continuous monitoring with automated threat detection',
    status: 'implemented',
    evidence: 'SOC monitoring reports',
    lastAudited: '2024-01-18'
  },
  {
    id: 'sc_006',
    category: 'Compliance',
    name: 'GDPR Compliance',
    description: 'Full compliance with General Data Protection Regulation',
    status: 'implemented',
    evidence: 'GDPR compliance certificate',
    lastAudited: '2023-12-30'
  }
];

const COMPLIANCE_STANDARDS: ComplianceStandard[] = [
  {
    id: 'cs_001',
    name: 'GDPR',
    description: 'General Data Protection Regulation',
    status: 'compliant',
    controls: SECURITY_CONTROLS.filter(c => c.category === 'Compliance' || c.category === 'Data Protection'),
    lastAudit: '2023-12-30',
    nextAudit: '2024-12-30'
  },
  {
    id: 'cs_002',
    name: 'SOC 2 Type II',
    description: 'Security, Availability, Processing Integrity, Confidentiality, and Privacy',
    status: 'in-progress',
    controls: SECURITY_CONTROLS,
    lastAudit: '2023-06-15',
    nextAudit: '2024-06-15'
  },
  {
    id: 'cs_003',
    name: 'ISO 27001',
    description: 'Information Security Management',
    status: 'in-progress',
    controls: SECURITY_CONTROLS.filter(c => c.category !== 'Compliance'),
    lastAudit: '2023-09-22',
    nextAudit: '2024-09-22'
  }
];

const MOCK_AUDIT_LOGS: AuditLog[] = [
  {
    id: 'al_001',
    action: 'User Login',
    user: 'admin@acme.com',
    timestamp: '2024-01-20T10:30:00Z',
    ipAddress: '203.0.113.1',
    details: 'Successful login with MFA'
  },
  {
    id: 'al_002',
    action: 'API Key Generated',
    user: 'dev@acme.com',
    timestamp: '2024-01-20T09:15:00Z',
    ipAddress: '203.0.113.2',
    details: 'Created new production API key with vault:read, vault:write permissions'
  },
  {
    id: 'al_003',
    action: 'Data Access',
    user: 'system',
    timestamp: '2024-01-20T08:45:00Z',
    ipAddress: '10.0.0.5',
    details: 'Vault data retrieved for processing request #req_12345'
  },
  {
    id: 'al_004',
    action: 'Security Alert',
    user: 'system',
    timestamp: '2024-01-20T07:22:00Z',
    ipAddress: '10.0.0.10',
    details: 'Unusual access pattern detected from IP 198.51.100.5, blocked automatically'
  }
];

export default function SecurityCompliance() {
  const [activeTab, setActiveTab] = useState<'controls' | 'compliance' | 'audit' | 'gdpr'>('controls');
  const [complianceMetrics, setComplianceMetrics] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>(MOCK_AUDIT_LOGS);

  // Load compliance metrics
  useEffect(() => {
    const loadComplianceMetrics = async () => {
      try {
        const metrics = gdprComplianceManager.getComplianceMetrics();
        setComplianceMetrics(metrics);
      } catch (error) {
        console.error('Failed to load compliance metrics:', error);
      }
    };

    loadComplianceMetrics();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'implemented': return 'bg-green-100 text-green-800';
      case 'compliant': return 'bg-green-100 text-green-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'planned': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getComplianceStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'bg-green-100 text-green-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'not-started': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Security & Compliance</h2>
          <p className="text-gray-600 mt-1">Manage security controls and compliance standards</p>
        </div>
        <div className="flex space-x-3">
          <button className="btn-secondary flex items-center">
            <DocumentTextIcon className="h-5 w-5 mr-2" />
            Download Report
          </button>
          <button className="btn-primary flex items-center">
            <ShieldCheckIcon className="h-5 w-5 mr-2" />
            Run Audit
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'controls', name: 'Security Controls', icon: LockClosedIcon },
            { id: 'compliance', name: 'Compliance Standards', icon: ShieldCheckIcon },
            { id: 'audit', name: 'Audit Logs', icon: ChartBarIcon },
            { id: 'gdpr', name: 'GDPR Dashboard', icon: KeyIcon }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security Controls Tab */}
      {activeTab === 'controls' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <LockClosedIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Implemented Controls</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {SECURITY_CONTROLS.filter(c => c.status === 'implemented').length}
                    <span className="text-sm font-normal text-gray-500">/{SECURITY_CONTROLS.length}</span>
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {SECURITY_CONTROLS.filter(c => c.status === 'in-progress').length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <ClockIcon className="h-6 w-6 text-gray-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Planned</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {SECURITY_CONTROLS.filter(c => c.status === 'planned').length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Security Controls</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Control</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Audited</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {SECURITY_CONTROLS.map((control) => (
                    <tr key={control.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{control.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{control.category}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">{control.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(control.status)}`}>
                          {control.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {control.lastAudited || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* Compliance Standards Tab */}
      {activeTab === 'compliance' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {COMPLIANCE_STANDARDS.map((standard) => (
              <div key={standard.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900">{standard.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getComplianceStatusColor(standard.status)}`}>
                      {standard.status}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-gray-600">{standard.description}</p>
                  
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Controls:</span>
                      <span className="font-medium text-gray-900">{standard.controls.length}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-600">Last Audit:</span>
                      <span className="font-medium text-gray-900">{standard.lastAudit || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-600">Next Audit:</span>
                      <span className="font-medium text-gray-900">{standard.nextAudit || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Compliance Controls</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Standard</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Control</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {COMPLIANCE_STANDARDS.flatMap(standard => 
                    standard.controls.map(control => (
                      <tr key={`${standard.id}-${control.id}`} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{standard.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{control.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{control.category}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(control.status)}`}>
                            {control.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* Audit Logs Tab */}
      {activeTab === 'audit' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Audit Logs</h3>
              <div className="flex space-x-3">
                <input
                  type="text"
                  placeholder="Search logs..."
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
                <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200">
                  Filter
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP Address</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{log.action}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{log.user}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{log.ipAddress}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">{log.details}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* GDPR Dashboard Tab */}
      {activeTab === 'gdpr' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {complianceMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DocumentTextIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Requests</p>
                    <p className="text-2xl font-bold text-gray-900">{complianceMetrics.requests.total}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <ClockIcon className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Pending Requests</p>
                    <p className="text-2xl font-bold text-gray-900">{complianceMetrics.requests.pending}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircleIcon className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{complianceMetrics.requests.completionRate}%</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Recent Breaches</p>
                    <p className="text-2xl font-bold text-gray-900">{complianceMetrics.breaches.recent}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Request Types</h3>
              </div>
              <div className="p-6">
                {complianceMetrics?.requests.byType && (
                  <div className="space-y-4">
                    {Object.entries(complianceMetrics.requests.byType).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 capitalize">{type}</span>
                        <span className="text-sm font-medium text-gray-900">{count as number}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 bg-green-500 rounded-full mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">Data access request fulfilled</p>
                      <p className="text-xs text-gray-500">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 bg-yellow-500 rounded-full mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">New erasure request received</p>
                      <p className="text-xs text-gray-500">1 day ago</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">Compliance audit completed</p>
                      <p className="text-xs text-gray-500">3 days ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Data Processing Records</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Controller</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Processing Activities</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Categories</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Retention</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">Acme Corporation</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-600">Storage, API processing, analytics</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">Identity, Contact, Technical</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">2 years</div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}