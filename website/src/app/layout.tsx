import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ReliQuary - Enterprise-Grade Cryptographic Memory Platform',
  description: 'Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs. Built for the quantum computing era.',
  keywords: 'cryptography, post-quantum, security, enterprise, multi-agent, consensus, zero-knowledge, blockchain',
  authors: [{ name: 'ReliQuary Team' }],
  creator: 'ReliQuary Team',
  publisher: 'ReliQuary',
  metadataBase: new URL('https://reliquary-kairoki.vercel.app'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'ReliQuary - Enterprise-Grade Cryptographic Memory Platform',
    description: 'Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs.',
    siteName: 'ReliQuary',
    images: [
      {
        url: '/og-image.svg',
        width: 1200,
        height: 630,
        alt: 'ReliQuary Platform Overview',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ReliQuary - Enterprise-Grade Cryptographic Memory Platform',
    description: 'Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs.',
    images: ['/twitter-image.png'],
    creator: '@reliquary',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
    other: {
      rel: 'apple-touch-icon-precomposed',
      url: '/apple-touch-icon-precomposed.png',
    },
  },
  manifest: '/site.webmanifest',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.className} dark:bg-gray-900 dark:text-white`}>
        {children}
        
        {/* Remove Google Analytics and Hotjar for now since we're testing */}
      </body>
    </html>
  )
}