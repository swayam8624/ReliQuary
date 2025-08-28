'use client';

import Link from 'next/link';
import { 
  ShieldCheckIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';
import {
  TwitterIcon,
  LinkedInIcon,
  GitHubIcon,
  YouTubeIcon,
  DiscordIcon
} from '@/components/SocialIcons';

const navigation = {
  product: [
    { name: 'Features', href: '/features' },
    { name: 'Security', href: '/security' },
    { name: 'Pricing', href: '/pricing' },
    { name: 'Integrations', href: '/integrations' },
    { name: 'Enterprise', href: '/enterprise' },
  ],
  developers: [
    { name: 'Documentation', href: '/docs' },
    { name: 'API Reference', href: '/api-reference' },
    { name: 'SDKs', href: '/sdks' },
    { name: 'Tutorials', href: '/tutorials' },
    { name: 'Examples', href: '/examples' },
  ],
  resources: [
    { name: 'Blog', href: '/blog' },
    { name: 'Case Studies', href: '/case-studies' },
    { name: 'Whitepapers', href: '/whitepapers' },
    { name: 'Webinars', href: '/webinars' },
    { name: 'Community', href: '/community' },
  ],
  company: [
    { name: 'About', href: '/about' },
    { name: 'Careers', href: '/careers' },
    { name: 'Press', href: '/press' },
    { name: 'Partners', href: '/partners' },
    { name: 'Contact', href: '/contact' },
  ],
  support: [
    { name: 'Help Center', href: '/help' },
    { name: 'Status Page', href: '/status' },
    { name: 'Bug Reports', href: '/bugs' },
    { name: 'Feature Requests', href: '/features' },
    { name: 'Professional Services', href: '/services' },
  ],
  legal: [
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Terms of Service', href: '/terms' },
    { name: 'Cookie Policy', href: '/cookies' },
    { name: 'Security', href: '/security' },
    { name: 'Compliance', href: '/compliance' },
  ],
};

const socialLinks = [
  {
    name: 'Twitter',
    href: 'https://twitter.com/reliquary',
    icon: TwitterIcon,
  },
  {
    name: 'LinkedIn',
    href: 'https://linkedin.com/company/reliquary',
    icon: LinkedInIcon,
  },
  {
    name: 'GitHub',
    href: 'https://github.com/reliquary',
    icon: GitHubIcon,
  },
  {
    name: 'YouTube',
    href: 'https://youtube.com/@reliquary',
    icon: YouTubeIcon,
  },
  {
    name: 'Discord',
    href: 'https://discord.gg/reliquary',
    icon: DiscordIcon,
  },
];

const certifications = [
  'SOC 2 Type II',
  'ISO 27001',
  'GDPR Compliant',
  'HIPAA Ready',
  'FedRAMP Ready'
];

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container-custom">
        
        {/* Main Footer Content */}
        <div className="py-16">
          <div className="grid lg:grid-cols-6 gap-8">
            
            {/* Company Info */}
            <div className="lg:col-span-2">
              <Link href="/" className="flex items-center space-x-3 mb-6">
                <ShieldCheckIcon className="h-8 w-8 text-primary-400" />
                <span className="text-xl font-bold">ReliQuary</span>
              </Link>
              
              <p className="text-gray-300 mb-6 max-w-md">
                Enterprise-grade cryptographic memory platform with post-quantum security, 
                multi-agent consensus, and zero-knowledge proofs. Built for the quantum computing era.
              </p>

              {/* Contact Info */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center space-x-3">
                  <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                  <a href="mailto:contact@reliquary.io" className="text-gray-300 hover:text-white transition-colors">
                    contact@reliquary.io
                  </a>
                </div>
                <div className="flex items-center space-x-3">
                  <PhoneIcon className="h-5 w-5 text-gray-400" />
                  <a href="tel:+1-555-RELIQUARY" className="text-gray-300 hover:text-white transition-colors">
                    +1 (555) RELIQUARY
                  </a>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPinIcon className="h-5 w-5 text-gray-400" />
                  <span className="text-gray-300">
                    San Francisco, CA & Remote
                  </span>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex space-x-4">
                {socialLinks.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <span className="sr-only">{item.name}</span>
                    <item.icon className="h-6 w-6" />
                  </a>
                ))}
              </div>
            </div>

            {/* Navigation Links */}
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-3">
                {navigation.product.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-gray-300 hover:text-white transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Developers</h3>
              <ul className="space-y-3">
                {navigation.developers.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-gray-300 hover:text-white transition-colors flex items-center space-x-1"
                    >
                      <span>{item.name}</span>
                      {item.name === 'API Reference' && (
                        <ArrowTopRightOnSquareIcon className="h-3 w-3" />
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-3">
                {navigation.resources.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-gray-300 hover:text-white transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-3 mb-6">
                {navigation.company.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-gray-300 hover:text-white transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>

              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-3">
                {navigation.support.slice(0, 3).map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-gray-300 hover:text-white transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Certifications */}
        <div className="py-8 border-t border-gray-800">
          <div className="text-center mb-6">
            <h4 className="font-semibold mb-4">Security & Compliance</h4>
            <div className="flex flex-wrap justify-center gap-4">
              {certifications.map((cert) => (
                <div
                  key={cert}
                  className="bg-gray-800 px-4 py-2 rounded-lg text-sm text-gray-300"
                >
                  {cert}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-8 border-t border-gray-800">
          <div className="flex flex-col lg:flex-row justify-between items-center space-y-4 lg:space-y-0">
            <div className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-6 text-sm text-gray-400">
              <span>© 2024 ReliQuary. All rights reserved.</span>
              <div className="flex items-center space-x-4">
                {navigation.legal.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className="hover:text-white transition-colors"
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <Link
                href="/status"
                className="flex items-center space-x-2 hover:text-white transition-colors"
              >
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>All Systems Operational</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Newsletter Signup */}
        <div className="py-8 border-t border-gray-800">
          <div className="max-w-md mx-auto text-center">
            <h4 className="font-semibold mb-2">Stay Updated</h4>
            <p className="text-gray-400 text-sm mb-4">
              Get the latest security insights and product updates.
            </p>
            <form className="flex space-x-2">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:outline-none"
              />
              <button
                type="submit"
                className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </div>
    </footer>
  );
}