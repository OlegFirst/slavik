import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BCM Platform - AI-Powered Business Continuity',
  description: 'Intelligent BCM platform with Digital Twin simulation and ISO 22301 compliance',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
