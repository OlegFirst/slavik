// Client-safe docs library - reads from pre-generated JSON
import docsData from '../../public/docs.json'

export interface Doc {
  slug: string
  title: string
  description?: string
  category: string
  tags?: string[]
  content: string
  lastModified?: string
  previousDoc?: { slug: string; title: string }
  nextDoc?: { slug: string; title: string }
}

export function getAllDocs(): Doc[] {
  return docsData as Doc[]
}

export function getDocBySlug(slug: string): Doc | null {
  const docs = getAllDocs()
  return docs.find((doc) => doc.slug === slug) || null
}

export function getDocsByCategory(category: string): Doc[] {
  const docs = getAllDocs()
  return docs.filter((doc) => doc.category === category)
}

export function searchDocs(query: string): Doc[] {
  const docs = getAllDocs()
  const lowerQuery = query.toLowerCase()

  return docs.filter((doc) => {
    return (
      doc.title.toLowerCase().includes(lowerQuery) ||
      doc.description?.toLowerCase().includes(lowerQuery) ||
      doc.content?.toLowerCase().includes(lowerQuery) ||
      doc.tags?.some((tag) => tag.toLowerCase().includes(lowerQuery))
    )
  })
}

export function getCategories(): { name: string; slug: string; icon: string }[] {
  return [
    { name: 'Architecture', slug: 'architecture', icon: 'Building2' },
    { name: 'Requirements', slug: 'requirements', icon: 'FileText' },
    { name: 'Design', slug: 'design', icon: 'Palette' },
    { name: 'Implementation', slug: 'implementation', icon: 'Code' },
    { name: 'Reports', slug: 'reports', icon: 'BarChart3' },
  ]
}
