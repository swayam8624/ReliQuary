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
  metadataBase: new URL('https://reliquary.io'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'ReliQuary - Enterprise-Grade Cryptographic Memory Platform',
    description: 'Secure, intelligent, and scalable cryptographic infrastructure with post-quantum security, multi-agent consensus, and zero-knowledge proofs.',
    url: 'https://reliquary.io',
    siteName: 'ReliQuary',
    images: [
      {
        url: '/og-image.png',
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
    icon: '/favicon.ico',
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
        
        {/* Analytics */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Google Analytics
              (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
              
              ga('create', 'UA-XXXXXXXXX-X', 'auto');
              ga('send', 'pageview');
            `,
          }}
        />
        
        {/* Hotjar */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function(h,o,t,j,a,r){
                h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
                h._hjSettings={hjid:XXXXXXX,hjsv:6};
                a=o.getElementsByTagName('head')[0];
                r=o.createElement('script');r.async=1;
                r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
                a.appendChild(r);
              })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
            `,
          }}
        />
      </body>
    </html>
  )
}