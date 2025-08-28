'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeftIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  PhoneIcon,
  QuestionMarkCircleIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function SupportPage() {
  const [activeTab, setActiveTab] = useState('help');
  const [ticketForm, setTicketForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    priority: 'medium'
  });

  const handleTicketSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real implementation, this would submit to an API
    alert('Support ticket submitted! Our team will get back to you soon.');
    setTicketForm({
      name: '',
      email: '',
      subject: '',
      message: '',
      priority: 'medium'
    });
  };

  const supportOptions = [
    {
      id: 'documentation',
      title: 'Documentation',
      description: 'Comprehensive guides and API references',
      icon: DocumentTextIcon,
      href: '/docs',
      cta: 'View Docs'
    },
    {
      id: 'community',
      title: 'Community Forum',
      description: 'Connect with other developers and get help',
      icon: ChatBubbleLeftRightIcon,
      href: '/community',
      cta: 'Join Forum'
    },
    {
      id: 'contact',
      title: 'Contact Sales',
      description: 'Talk to our sales team about enterprise solutions',
      icon: PhoneIcon,
      href: '/contact',
      cta: 'Contact Us'
    }
  ];

  const faqs = [
    {
      question: 'How do I get started with ReliQuary?',
      answer: 'Check out our Quick Start Guide in the documentation section. You can also sign up for a free account and explore our interactive tutorials.'
    },
    {
      question: 'What are the system requirements?',
      answer: 'ReliQuary works with Python 3.8+, Node.js 14+, Java 11+, and Go 1.19+. For self-hosting, you\'ll need Docker or Kubernetes.'
    },
    {
      question: 'How do I report a security vulnerability?',
      answer: 'Please contact our security team directly at security@reliquary.io with details about the vulnerability. We appreciate responsible disclosure.'
    },
    {
      question: 'Do you offer enterprise support?',
      answer: 'Yes, our Enterprise plan includes 24/7 support, a dedicated success manager, and custom SLA options. Contact sales for more information.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2">
              <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Back to Home</span>
            </Link>
            <h1 className="text-xl font-semibold text-gray-900">Support Center</h1>
            <div></div> {/* Spacer for alignment */}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-gray-900 mb-4"
          >
            How can we help you?
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Get help with ReliQuary through documentation, community support, or direct assistance from our team.
          </motion.p>
        </div>

        {/* Support Options */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {supportOptions.map((option, index) => (
            <motion.div
              key={option.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <option.icon className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="ml-3 text-lg font-semibold text-gray-900">{option.title}</h3>
              </div>
              <p className="text-gray-600 mb-4">{option.description}</p>
              <Link 
                href={option.href}
                className="inline-flex items-center text-primary-600 font-medium hover:text-primary-700"
              >
                {option.cta}
                <ArrowLeftIcon className="h-4 w-4 ml-1 rotate-180" />
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('help')}
                className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                  activeTab === 'help'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Help Center
              </button>
              <button
                onClick={() => setActiveTab('ticket')}
                className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                  activeTab === 'ticket'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Submit Ticket
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'help' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
                
                <div className="space-y-6">
                  {faqs.map((faq, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-5 hover:shadow-sm transition-shadow">
                      <h3 className="font-semibold text-gray-900 mb-2">{faq.question}</h3>
                      <p className="text-gray-600">{faq.answer}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-100">
                  <div className="flex items-start">
                    <QuestionMarkCircleIcon className="h-6 w-6 text-blue-500 mt-1 flex-shrink-0" />
                    <div className="ml-4">
                      <h3 className="font-semibold text-gray-900 mb-2">Can't find what you're looking for?</h3>
                      <p className="text-gray-600 mb-4">
                        Our support team is here to help. Submit a ticket and we'll get back to you within 24 hours.
                      </p>
                      <button
                        onClick={() => setActiveTab('ticket')}
                        className="btn-primary"
                      >
                        Submit Support Ticket
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'ticket' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Submit Support Ticket</h2>
                <p className="text-gray-600 mb-6">
                  Need direct assistance? Fill out this form and our support team will contact you.
                </p>
                
                <form onSubmit={handleTicketSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                        Full Name
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <UserIcon className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          type="text"
                          id="name"
                          value={ticketForm.name}
                          onChange={(e) => setTicketForm({...ticketForm, name: e.target.value})}
                          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                          placeholder="Your name"
                          required
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                        Email Address
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          type="email"
                          id="email"
                          value={ticketForm.email}
                          onChange={(e) => setTicketForm({...ticketForm, email: e.target.value})}
                          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                          placeholder="your.email@example.com"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                      Subject
                    </label>
                    <input
                      type="text"
                      id="subject"
                      value={ticketForm.subject}
                      onChange={(e) => setTicketForm({...ticketForm, subject: e.target.value})}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Brief description of your issue"
                      required
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                      Priority
                    </label>
                    <select
                      id="priority"
                      value={ticketForm.priority}
                      onChange={(e) => setTicketForm({...ticketForm, priority: e.target.value})}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="low">Low - General inquiry</option>
                      <option value="medium">Medium - Issue affecting productivity</option>
                      <option value="high">High - System down or critical issue</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="message"
                      rows={5}
                      value={ticketForm.message}
                      onChange={(e) => setTicketForm({...ticketForm, message: e.target.value})}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Please provide detailed information about your issue..."
                      required
                    />
                  </div>
                  
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="btn-primary"
                    >
                      Submit Ticket
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>

        {/* Contact Info */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Prefer to contact us directly? Email{' '}
            <a href="mailto:support@reliquary.io" className="text-primary-600 hover:text-primary-700">
              support@reliquary.io
            </a>{' '}
            or call{' '}
            <a href="tel:+15551234567" className="text-primary-600 hover:text-primary-700">
              +1 (555) 123-4567
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}