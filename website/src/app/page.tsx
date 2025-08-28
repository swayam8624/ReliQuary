'use client';

import { useEffect } from 'react';
import Head from 'next/head';
import Header from '@/components/Header';
import Hero from '@/components/Hero';
import Features from '@/components/Features';
import Pricing from '@/components/Pricing';
import Testimonials from '@/components/Testimonials';
import CTA from '@/components/CTA';
import Footer from '@/components/Footer';

export default function LandingPage() {
  useEffect(() => {
    // Smooth scroll behavior for anchor links
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash) {
        const element = document.querySelector(hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // Handle initial hash

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return (
    <>
      <Head>
        <title>ReliQuary - Enterprise-Grade Cryptographic Memory Platform</title>
        <meta 
          name="description" 
          content="Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs. Built for the quantum computing era." 
        />
        <meta name="keywords" content="cryptography, post-quantum, security, enterprise, multi-agent, consensus, zero-knowledge, blockchain" />
        <meta name="author" content="ReliQuary Team" />
        
        {/* Open Graph */}
        <meta property="og:title" content="ReliQuary - Enterprise-Grade Cryptographic Memory Platform" />
        <meta property="og:description" content="Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://reliquary.io" />
        <meta property="og:image" content="https://reliquary.io/og-image.png" />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="ReliQuary - Enterprise-Grade Cryptographic Memory Platform" />
        <meta name="twitter:description" content="Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs." />
        <meta name="twitter:image" content="https://reliquary.io/twitter-image.png" />
        
        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        
        {/* Canonical URL */}
        <link rel="canonical" href="https://reliquary.io" />
        
        {/* Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "ReliQuary",
              "description": "Enterprise-Grade Cryptographic Memory Platform",
              "url": "https://reliquary.io",
              "applicationCategory": "SecurityApplication",
              "operatingSystem": "Cross-platform",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "description": "Free tier available"
              },
              "creator": {
                "@type": "Organization",
                "name": "ReliQuary Team"
              }
            })
          }}
        />
      </Head>

      <div className="min-h-screen bg-white">
        <Header />
        
        <main>
          <Hero />
          <Features />
          <Pricing />
          <Testimonials />
          <CTA />
        </main>
        
        <Footer />
      </div>
    </>
  );
}