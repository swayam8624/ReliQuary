'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  BuildingOfficeIcon, 
  ChartBarIcon, 
  ShieldCheckIcon,
  ArrowRightIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';

const caseStudies = [
  {
    id: 1,
    company: 'FinTech Corp',
    industry: 'Financial Services',
    challenge: 'Securing high-volume transactions against quantum threats',
    solution: 'Implemented ReliQuary\'s post-quantum cryptographic platform',
    results: '99.99% uptime, $2B secured transactions, 50% reduction in security incidents',
    logo: 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    metrics: [
      { label: 'Transactions Secured', value: '$2B+' },
      { label: 'Security Incidents', value: '-50%' },
      { label: 'System Uptime', value: '99.99%' }
    ]
  },
  {
    id: 2,
    company: 'HealthSecure Inc',
    industry: 'Healthcare',
    challenge: 'Complying with HIPAA while enabling real-time data sharing',
    solution: 'Deployed zero-knowledge architecture with threshold cryptography',
    results: 'Full HIPAA compliance, 40% faster data processing, zero data breaches',
    logo: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    metrics: [
      { label: 'Data Processing', value: '+40%' },
      { label: 'Compliance', value: '100%' },
      { label: 'Breaches', value: '0' }
    ]
  },
  {
    id: 3,
    company: 'GovCloud Solutions',
    industry: 'Government',
    challenge: 'Building a secure cloud infrastructure for classified data',
    solution: 'Multi-agent consensus system with air-gapped key management',
    results: 'Enhanced security posture, 60% reduction in audit findings, accelerated deployment',
    logo: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    metrics: [
      { label: 'Audit Findings', value: '-60%' },
      { label: 'Deployment Time', value: '-30%' },
      { label: 'Security Rating', value: 'A+' }
    ]
  },
  {
    id: 4,
    company: 'RetailChain Global',
    industry: 'Retail',
    challenge: 'Protecting customer data across global supply chain',
    solution: 'Distributed cryptographic memory with real-time monitoring',
    results: 'Zero customer data breaches, 75% improvement in supply chain efficiency, enhanced customer trust',
    logo: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
    metrics: [
      { label: 'Data Breaches', value: '0' },
      { label: 'Supply Chain', value: '+75%' },
      { label: 'Customer Trust', value: '+40%' }
    ]
  }
];

export default function CaseStudiesPage() {
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
                Customer Success Stories
              </h1>
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-10">
                See how organizations across industries leverage ReliQuary to solve complex 
                security challenges and achieve their business objectives.
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Case Studies */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="grid grid-cols-1 gap-12">
            {caseStudies.map((study, index) => (
              <motion.div
                key={study.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700"
              >
                <div className="md:flex">
                  <div className="md:w-1/3 p-8 flex flex-col items-center justify-center bg-gradient-to-br from-primary-500 to-accent-500 text-white">
                    <img 
                      src={study.logo} 
                      alt={`${study.company} logo`} 
                      className="h-16 w-16 rounded-full mb-6 object-cover"
                    />
                    <h3 className="text-2xl font-bold mb-2">{study.company}</h3>
                    <p className="text-primary-100 mb-4">{study.industry}</p>
                    <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-white/20 text-white">
                      <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                      Enterprise
                    </div>
                  </div>
                  
                  <div className="md:w-2/3 p-8">
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Challenge</h4>
                      <p className="text-gray-600 dark:text-gray-400">{study.challenge}</p>
                    </div>
                    
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Solution</h4>
                      <p className="text-gray-600 dark:text-gray-400">{study.solution}</p>
                    </div>
                    
                    <div className="mb-8">
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Results</h4>
                      <p className="text-gray-600 dark:text-gray-400 mb-4">{study.results}</p>
                      
                      <div className="grid grid-cols-3 gap-4">
                        {study.metrics.map((metric, metricIndex) => (
                          <div key={metricIndex} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{metric.value}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">{metric.label}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-3">
                      <Link 
                        href={`/case-studies/${study.id}`}
                        className="btn-primary inline-flex items-center"
                      >
                        Read Full Case Study
                        <ArrowRightIcon className="ml-2 h-5 w-5" />
                      </Link>
                      <button className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center">
                        <UserGroupIcon className="h-5 w-5 mr-2" />
                        Contact Customer
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="py-16 lg:py-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 dark:text-white mb-4">
              What Our Customers Say
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Hear directly from our customers about their experience with ReliQuary.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                quote: "ReliQuary transformed our security infrastructure. The post-quantum algorithms gave us confidence that our systems will remain secure even as technology evolves.",
                author: "Sarah Johnson",
                role: "CTO, FinTech Corp",
                avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=100&q=80"
              },
              {
                quote: "The zero-knowledge architecture allowed us to comply with strict regulations while still enabling real-time data sharing across our organization.",
                author: "Michael Chen",
                role: "Security Director, HealthSecure Inc",
                avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=100&q=80"
              },
              {
                quote: "Implementing ReliQuary reduced our audit findings by 60% and gave us the security posture we needed for handling classified government data.",
                author: "Robert Williams",
                role: "Director, GovCloud Solutions",
                avatar: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=100&q=80"
              }
            ].map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="text-yellow-400 mb-4">
                  {'★'.repeat(5)}
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-6 italic">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center">
                  <img 
                    src={testimonial.avatar} 
                    alt={testimonial.author} 
                    className="h-10 w-10 rounded-full mr-3 object-cover"
                  />
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">{testimonial.author}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{testimonial.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 lg:py-24 bg-white dark:bg-gray-900">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl p-12 text-white">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Transform Your Security Infrastructure?
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Join hundreds of organizations that trust ReliQuary for their most critical security needs.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link 
                href="/contact" 
                className="btn-primary bg-white text-primary-600 hover:bg-gray-100"
              >
                Schedule a Demo
              </Link>
              <Link 
                href="/pricing" 
                className="btn-secondary bg-transparent border-white text-white hover:bg-white/10"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}