'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  StarIcon,
  QuoteLeftIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

const testimonials = [
  {
    id: 1,
    name: 'Sarah Chen',
    role: 'CISO',
    company: 'TechCorp Financial',
    avatar: '/avatars/sarah-chen.jpg',
    rating: 5,
    quote: 'ReliQuary transformed our security posture completely. The post-quantum cryptography gives us confidence that our data will remain secure even in the quantum computing era.',
    metrics: {
      implementation: '2 weeks',
      improvement: '99.8% threat reduction',
      compliance: 'SOC 2 Type II'
    }
  },
  {
    id: 2,
    name: 'Dr. Michael Rodriguez',
    role: 'Head of Engineering',
    company: 'HealthSecure Inc.',
    avatar: '/avatars/michael-rodriguez.jpg',
    rating: 5,
    quote: 'The multi-agent consensus system is brilliant. It provides an extra layer of security for our patient data while maintaining compliance with HIPAA regulations.',
    metrics: {
      implementation: '1 week',
      improvement: '60% faster decisions',
      compliance: 'HIPAA Compliant'
    }
  },
  {
    id: 3,
    name: 'James Patterson',
    role: 'VP of Technology',
    company: 'Global Manufacturing Ltd.',
    avatar: '/avatars/james-patterson.jpg',
    rating: 5,
    quote: 'Scaling across our global operations was seamless. The enterprise features and 99.99% uptime SLA give us the reliability we need for mission-critical applications.',
    metrics: {
      implementation: '3 weeks',
      improvement: '40% cost reduction',
      compliance: 'ISO 27001'
    }
  },
  {
    id: 4,
    name: 'Lisa Thompson',
    role: 'CTO',
    company: 'FinTech Innovations',
    avatar: '/avatars/lisa-thompson.jpg',
    rating: 5,
    quote: 'Zero-knowledge proofs have revolutionized our KYC process. We can verify customer credentials without compromising privacy - exactly what the financial industry needs.',
    metrics: {
      implementation: '10 days',
      improvement: '85% faster KYC',
      compliance: 'PCI DSS Level 1'
    }
  },
  {
    id: 5,
    name: 'Robert Kim',
    role: 'Security Architect',
    company: 'Enterprise Solutions Corp',
    avatar: '/avatars/robert-kim.jpg',
    rating: 5,
    quote: 'The threshold cryptography implementation is outstanding. We can distribute our most sensitive operations across multiple secure environments with confidence.',
    metrics: {
      implementation: '2.5 weeks',
      improvement: '95% risk reduction',
      compliance: 'FedRAMP Ready'
    }
  }
];

const companies = [
  { name: 'TechCorp', logo: '/logos/techcorp.svg' },
  { name: 'HealthSecure', logo: '/logos/healthsecure.svg' },
  { name: 'Global Manufacturing', logo: '/logos/global-mfg.svg' },
  { name: 'FinTech Innovations', logo: '/logos/fintech-innov.svg' },
  { name: 'Enterprise Solutions', logo: '/logos/enterprise-sol.svg' },
  { name: 'SecureBank', logo: '/logos/securebank.svg' },
  { name: 'DataVault', logo: '/logos/datavault.svg' },
  { name: 'CryptoSafe', logo: '/logos/cryptosafe.svg' }
];

const stats = [
  { value: '500+', label: 'Enterprise Customers' },
  { value: '99.99%', label: 'Uptime Achievement' },
  { value: '10M+', label: 'Secure Operations Daily' },
  { value: '50+', label: 'Countries Deployed' }
];

export default function Testimonials() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <StarIconSolid
        key={i}
        className={`h-5 w-5 ${i < rating ? 'text-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <section className="section-padding bg-gradient-to-b from-gray-50 to-white">
      <div className="container-custom">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <h2 className="heading-lg text-gray-900 mb-6">
            Trusted by Industry Leaders
          </h2>
          <p className="text-large text-gray-600">
            See how leading organizations are transforming their security posture with ReliQuary's 
            enterprise-grade cryptographic platform.
          </p>
        </motion.div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16"
        >
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">{stat.value}</div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Main Testimonial */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="relative max-w-4xl mx-auto mb-16"
        >
          <div className="bg-white rounded-2xl shadow-xl p-8 lg:p-12">
            <div className="absolute -top-6 left-8">
              <div className="bg-primary-500 text-white p-4 rounded-full">
                <QuoteLeftIcon className="h-8 w-8" />
              </div>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentTestimonial}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {/* Stars */}
                <div className="flex space-x-1">
                  {renderStars(testimonials[currentTestimonial].rating)}
                </div>

                {/* Quote */}
                <blockquote className="text-xl lg:text-2xl text-gray-900 leading-relaxed">
                  "{testimonials[currentTestimonial].quote}"
                </blockquote>

                {/* Author */}
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {testimonials[currentTestimonial].name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">
                      {testimonials[currentTestimonial].name}
                    </div>
                    <div className="text-gray-600">
                      {testimonials[currentTestimonial].role}
                    </div>
                    <div className="text-primary-600 font-medium">
                      {testimonials[currentTestimonial].company}
                    </div>
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t border-gray-100">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">
                      {testimonials[currentTestimonial].metrics.implementation}
                    </div>
                    <div className="text-sm text-gray-600">Implementation Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {testimonials[currentTestimonial].metrics.improvement}
                    </div>
                    <div className="text-sm text-gray-600">Performance Improvement</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-600">
                      {testimonials[currentTestimonial].metrics.compliance}
                    </div>
                    <div className="text-sm text-gray-600">Compliance Achievement</div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-8">
              <button
                onClick={prevTestimonial}
                className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                aria-label="Previous testimonial"
              >
                <ChevronLeftIcon className="h-6 w-6 text-gray-600" />
              </button>

              <div className="flex space-x-2">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentTestimonial(index)}
                    className={`w-3 h-3 rounded-full transition-colors ${
                      index === currentTestimonial ? 'bg-primary-600' : 'bg-gray-300'
                    }`}
                    aria-label={`Go to testimonial ${index + 1}`}
                  />
                ))}
              </div>

              <button
                onClick={nextTestimonial}
                className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                aria-label="Next testimonial"
              >
                <ChevronRightIcon className="h-6 w-6 text-gray-600" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Company Logos */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center"
        >
          <h3 className="text-lg font-semibold text-gray-600 mb-8">
            Trusted by leading organizations worldwide
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-8 items-center opacity-60">
            {companies.map((company, index) => (
              <div key={index} className="flex items-center justify-center">
                <div className="w-24 h-12 bg-gray-300 rounded-lg flex items-center justify-center">
                  <span className="text-xs font-medium text-gray-600">
                    {company.name}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Additional Testimonials Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mt-16"
        >
          {testimonials.slice(0, 3).map((testimonial, index) => (
            <div key={testimonial.id} className="card">
              <div className="flex space-x-1 mb-4">
                {renderStars(testimonial.rating)}
              </div>
              
              <blockquote className="text-gray-600 mb-6">
                "{testimonial.quote.substring(0, 120)}..."
              </blockquote>
              
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  {testimonial.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <div className="font-semibold text-gray-900 text-sm">
                    {testimonial.name}
                  </div>
                  <div className="text-xs text-gray-600">
                    {testimonial.role}, {testimonial.company}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}