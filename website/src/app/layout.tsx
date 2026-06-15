import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ReliQuary - Context-Bound Secret Vault',
  description: 'An open-source research system for context-bound cryptographic memory, vault access, audit trails, and trust-aware secret release.',
  keywords: 'cryptography, secrets, vault, access control, audit log, zero-knowledge',
  authors: [{ name: 'ReliQuary contributors' }],
  creator: 'ReliQuary contributors',
  publisher: 'ReliQuary',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
