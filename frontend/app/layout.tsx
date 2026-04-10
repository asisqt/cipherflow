import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CipherFlow — Secure Data Processing Pipeline',
  description: 'Enterprise-grade data validation, normalization, redaction, and encryption via API. Built with FastAPI, deployed on Kubernetes.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-50 antialiased">
        {children}
      </body>
    </html>
  )
}
