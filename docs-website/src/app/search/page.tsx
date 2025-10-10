import { DocSearch } from '@/components/DocSearch'

export const metadata = {
  title: 'Search Documentation | AI-Platform-ISO',
  description: 'Search through all technical documentation',
}

export default function SearchPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-4xl font-bold mb-8">Search Documentation</h1>
      <DocSearch />
    </div>
  )
}
