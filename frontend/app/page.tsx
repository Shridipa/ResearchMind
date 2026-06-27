import { Metadata } from 'next'
import LandingPageClient from '@/components/LandingPageClient'

export const metadata: Metadata = {
  title: 'ResearchMind AI — Grounded AI Research Workspace',
  description:
    'Upload academic papers, build semantic indexes, retrieve evidence-backed answers, compare research, and evaluate retrieval quality. A local-first research intelligence platform.',
}

export default function LandingPage() {
  return <LandingPageClient />
}
