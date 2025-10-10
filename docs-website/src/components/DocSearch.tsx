'use client'

import { useState, useMemo } from 'react'
import { getAllDocs } from '@/lib/docs'
import Link from 'next/link'
import { Search, FileText, Tag } from 'lucide-react'

export function DocSearch() {
  const [query, setQuery] = useState('')
  const docs = getAllDocs()

  const filteredDocs = useMemo(() => {
    if (!query.trim()) {
      return docs
    }

    const searchTerm = query.toLowerCase()
    return docs.filter((doc) => {
      const titleMatch = doc.title.toLowerCase().includes(searchTerm)
      const descriptionMatch = doc.description?.toLowerCase().includes(searchTerm)
      const contentMatch = doc.content.toLowerCase().includes(searchTerm)
      const tagMatch = doc.tags?.some((tag) => tag.toLowerCase().includes(searchTerm))

      return titleMatch || descriptionMatch || contentMatch || tagMatch
    })
  }, [query, docs])

  return (
    <div className="space-y-6">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search documentation..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        {query ? (
          <span>
            Found {filteredDocs.length} result{filteredDocs.length !== 1 ? 's' : ''} for "{query}"
          </span>
        ) : (
          <span>Showing all {docs.length} documents</span>
        )}
      </div>

      {/* Results */}
      <div className="space-y-4">
        {filteredDocs.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No documents found matching your search.</p>
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <Link
              key={doc.slug}
              href={`/docs/${doc.slug}`}
              className="block bg-card border rounded-lg p-4 hover:shadow-md transition-all hover:border-primary"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-lg font-semibold hover:text-primary transition-colors">
                  {doc.title}
                </h3>
                <FileText className="w-5 h-5 text-muted-foreground flex-shrink-0 ml-4" />
              </div>

              {doc.description && (
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                  {doc.description}
                </p>
              )}

              <div className="flex gap-2 flex-wrap items-center">
                <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded capitalize">
                  {doc.category}
                </span>
                {doc.tags && doc.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="flex items-center gap-1 text-xs px-2 py-1 bg-muted text-muted-foreground rounded">
                    <Tag className="w-3 h-3" />
                    {tag}
                  </span>
                ))}
                {doc.lastModified && (
                  <span className="text-xs text-muted-foreground ml-auto">
                    Updated {new Date(doc.lastModified).toLocaleDateString()}
                  </span>
                )}
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  )
}
