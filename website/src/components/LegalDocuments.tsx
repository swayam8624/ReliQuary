// Legal Documents Component
// Displays Terms of Service, Privacy Policy, and other legal documents

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  DocumentTextIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  ClockIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

interface LegalDocument {
  id: string;
  title: string;
  lastUpdated: string;
  icon: React.ComponentType<any>;
  content: string;
}

const LEGAL_DOCUMENTS: LegalDocument[] = [
  {
    id: 'terms',
    title: 'Terms of Service',
    lastUpdated: 'January 20, 2024',
    icon: DocumentTextIcon,
    content: `
      <h2>1. Introduction</h2>
      <p>Welcome to ReliQuary. These Terms of Service ("Terms") govern your access to and use of our services, including our website, APIs, and software (collectively, the "Services"). By accessing or using our Services, you agree to be bound by these Terms and our Privacy Policy.</p>
      
      <h2>2. Services</h2>
      <p>ReliQuary provides enterprise-grade cryptographic memory platform services, including but not limited to:</p>
      <ul>
        <li>Secure data storage and retrieval</li>
        <li>Post-quantum cryptographic operations</li>
        <li>Multi-agent consensus systems</li>
        <li>Zero-knowledge proof verification</li>
        <li>API access and integration tools</li>
      </ul>
      
      <h2>3. Account Registration</h2>
      <p>To access certain features of our Services, you may be required to register for an account. You agree to provide accurate, current, and complete information during registration and to update such information as necessary.</p>
      
      <h2>4. Acceptable Use</h2>
      <p>You agree not to use the Services for any unlawful purpose or in any way that could damage, disable, overburden, or impair our servers or networks. You shall not attempt to gain unauthorized access to any of the Services, other accounts, computer systems, or networks connected to any ReliQuary server.</p>
      
      <h2>5. Intellectual Property</h2>
      <p>The Services and all materials therein or transferred thereby, including, without limitation, software, images, text, graphics, illustrations, logos, patents, trademarks, service marks, copyrights, photographs, audio, videos, music, and other content (collectively, "ReliQuary Content"), are the exclusive property of ReliQuary and its licensors.</p>
      
      <h2>6. Data Processing and GDPR Compliance</h2>
      <p>ReliQuary acts as a data processor for customer data. We implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including encryption, pseudonymization, and regular testing of security measures.</p>
      
      <h2>7. Termination</h2>
      <p>We may terminate or suspend your account and bar access to the Services immediately, without prior notice or liability, under our sole discretion, for any reason whatsoever and without limitation, including but not limited to a breach of the Terms.</p>
      
      <h2>8. Limitation of Liability</h2>
      <p>In no event shall ReliQuary, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the Services.</p>
      
      <h2>9. Changes to Terms</h2>
      <p>We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material, we will provide at least 30 days' notice prior to any new terms taking effect.</p>
      
      <h2>10. Contact Us</h2>
      <p>If you have any questions about these Terms, please contact us at legal@reliquary.io.</p>
    `
  },
  {
    id: 'privacy',
    title: 'Privacy Policy',
    lastUpdated: 'January 20, 2024',
    icon: ShieldCheckIcon,
    content: `
      <h2>1. Introduction</h2>
      <p>ReliQuary ("we", "us", or "our") respects your privacy and is committed to protecting your personal data. This Privacy Policy explains how we collect, use, and share information about you when you use our services.</p>
      
      <h2>2. Information We Collect</h2>
      <p>We collect information you provide directly to us, such as when you create an account, contact us, or otherwise communicate with us. This may include:</p>
      <ul>
        <li>Identity and contact data (name, email address, phone number)</li>
        <li>Professional data (job title, company name, business contact details)</li>
        <li>Financial data (payment card information, billing address)</li>
        <li>Technical data (IP address, browser type, time zone, operating system)</li>
        <li>Usage data (how you interact with our services)</li>
      </ul>
      
      <h2>3. How We Use Your Information</h2>
      <p>We use your information to:</p>
      <ul>
        <li>Provide, maintain, and improve our services</li>
        <li>Process transactions and send transactional messages</li>
        <li>Send you technical notices, updates, and security alerts</li>
        <li>Respond to your comments, questions, and requests</li>
        <li>Monitor and analyze trends, usage, and activities</li>
        <li>Detect, investigate, and prevent fraudulent transactions and other illegal activities</li>
      </ul>
      
      <h2>4. Data Sharing and Disclosure</h2>
      <p>We may share your information with:</p>
      <ul>
        <li>Service providers who perform services on our behalf</li>
        <li>Professional advisors (lawyers, accountants, etc.)</li>
        <li>Law enforcement or regulatory authorities when required by law</li>
        <li>Corporate affiliates and subsidiaries</li>
      </ul>
      
      <h2>5. Data Security</h2>
      <p>We implement appropriate technical and organizational measures to protect your personal data, including encryption, access controls, and regular security assessments. All data is processed using post-quantum cryptographic algorithms.</p>
      
      <h2>6. Data Retention</h2>
      <p>We retain your personal data for as long as necessary to provide our services and fulfill the purposes outlined in this policy, unless a longer retention period is required or permitted by law.</p>
      
      <h2>7. Your Rights</h2>
      <p>Depending on your location, you may have certain rights regarding your personal data, including the right to access, correct, delete, or restrict the processing of your data.</p>
      
      <h2>8. International Data Transfers</h2>
      <p>Your information may be transferred to and maintained on computers located outside of your state, province, country, or other governmental jurisdiction where the data protection laws may differ from those in your jurisdiction.</p>
      
      <h2>9. Children's Privacy</h2>
      <p>Our services are not intended for individuals under the age of 16. We do not knowingly collect personal information from children under 16.</p>
      
      <h2>10. Changes to This Privacy Policy</h2>
      <p>We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.</p>
      
      <h2>11. Contact Us</h2>
      <p>If you have any questions about this Privacy Policy, please contact us at privacy@reliquary.io.</p>
    `
  },
  {
    id: 'dpa',
    title: 'Data Processing Agreement',
    lastUpdated: 'January 20, 2024',
    icon: BuildingOfficeIcon,
    content: `
      <h2>1. Introduction</h2>
      <p>This Data Processing Agreement ("DPA") supplements the Terms of Service between ReliQuary and the customer ("Customer") and governs the processing of personal data by ReliQuary on behalf of the Customer.</p>
      
      <h2>2. Definitions</h2>
      <p>Capitalized terms not defined in this DPA shall have the meanings given to them in the Terms of Service. "Personal Data", "Processing", and "Controller" shall have the meanings given to them in the GDPR.</p>
      
      <h2>3. Scope and Purpose of Processing</h2>
      <p>ReliQuary processes Personal Data only as described in this DPA and as necessary to provide the Services. The subject matter, duration, nature, and purpose of processing, as well as the types of Personal Data and categories of data subjects, are set forth in Exhibit A.</p>
      
      <h2>4. Documented Instructions</h2>
      <p>ReliQuary shall process Personal Data only on documented instructions from the Customer, including with regard to transfers of Personal Data to a third country or an international organization, unless required to do so by Union or Member State law to which ReliQuary is subject.</p>
      
      <h2>5. Confidentiality</h2>
      <p>ReliQuary shall ensure that persons authorized to process Personal Data have committed themselves to confidentiality or are under an appropriate statutory obligation of confidentiality.</p>
      
      <h2>6. Security Measures</h2>
      <p>ReliQuary shall implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including encryption, pseudonymization, and regular testing of security measures.</p>
      
      <h2>7. Subprocessing</h2>
      <p>ReliQuary shall not engage subprocessors without the prior written consent of the Customer. ReliQuary remains liable for the acts and omissions of any subprocessor as if it were liable for its own acts and omissions.</p>
      
      <h2>8. Data Subject Rights</h2>
      <p>ReliQuary shall assist the Customer in fulfilling its obligations to respond to requests from data subjects seeking to exercise their rights under applicable data protection laws.</p>
      
      <h2>9. Data Breach Notification</h2>
      <p>ReliQuary shall notify the Customer without undue delay after becoming aware of a Personal Data breach. The notification shall include sufficient information to allow the Customer to meet its obligations to notify supervisory authorities and data subjects.</p>
      
      <h2>10. Deletion or Return of Data</h2>
      <p>At the end of the provision of services, ReliQuary shall, at the Customer's choice, delete all Personal Data or return it to the Customer, unless Union or Member State law requires storage of the Personal Data.</p>
      
      <h2>11. Audit Rights</h2>
      <p>The Customer may request information and documentation from ReliQuary to demonstrate compliance with this DPA. ReliQuary shall provide reasonable cooperation and assistance in response to such requests.</p>
    `
  }
];

export default function LegalDocuments() {
  const [selectedDocument, setSelectedDocument] = useState<string>('terms');

  const currentDocument = LEGAL_DOCUMENTS.find(doc => doc.id === selectedDocument) || LEGAL_DOCUMENTS[0];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Legal Documents</h1>
        <p className="text-gray-600">Last updated: {currentDocument.lastUpdated}</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Document Navigation */}
        <div className="lg:w-1/3">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Documents</h2>
            <nav className="space-y-2">
              {LEGAL_DOCUMENTS.map((doc) => {
                const Icon = doc.icon;
                return (
                  <button
                    key={doc.id}
                    onClick={() => setSelectedDocument(doc.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      selectedDocument === doc.id
                        ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    <span className="font-medium">{doc.title}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Document Content */}
        <div className="lg:w-2/3">
          <motion.div
            key={selectedDocument}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200"
          >
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3 mb-2">
                {currentDocument.icon && <currentDocument.icon className="h-6 w-6 text-primary-600" />}
                <h2 className="text-2xl font-bold text-gray-900">{currentDocument.title}</h2>
              </div>
              <p className="text-gray-600">Last updated: {currentDocument.lastUpdated}</p>
            </div>
            
            <div className="p-6">
              <div 
                className="prose max-w-none legal-content"
                dangerouslySetInnerHTML={{ __html: currentDocument.content }}
              />
            </div>
          </motion.div>
        </div>
      </div>

      <style jsx>{`
        .legal-content h2 {
          font-size: 1.5rem;
          font-weight: 600;
          margin-top: 2rem;
          margin-bottom: 1rem;
          color: #111827;
        }
        
        .legal-content p {
          margin-bottom: 1rem;
          line-height: 1.75;
          color: #374151;
        }
        
        .legal-content ul {
          list-style-type: disc;
          margin-left: 1.5rem;
          margin-bottom: 1rem;
        }
        
        .legal-content li {
          margin-bottom: 0.5rem;
          line-height: 1.75;
          color: #374151;
        }
      `}</style>
    </div>
  );
}