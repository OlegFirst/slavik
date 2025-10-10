import { notFound } from 'next/navigation'
import { getDocBySlug, getAllDocs } from '@/lib/docs'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { TableOfContents } from '@/components/TableOfContents'
import { Breadcrumbs } from '@/components/Breadcrumbs'
import { FileText, Calendar, Tag } from 'lucide-react'

export async function generateStaticParams() {
  const docs = getAllDocs()
  return docs.map((doc) => ({
    slug: doc.slug.split('/'),
  }))
}

export async function generateMetadata({ params }: { params: { slug: string[] } }) {
  const doc = getDocBySlug(params.slug.join('/'))

  if (!doc) {
    return {
      title: 'Document Not Found',
    }
  }

  return {
    title: `${doc.title} | AI-Platform-ISO Documentation`,
    description: doc.description || `Documentation for ${doc.title}`,
  }
}

export default function DocPage({ params }: { params: { slug: string[] } }) {
  const slug = params.slug.join('/')
  const doc = getDocBySlug(slug)

  if (!doc) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Breadcrumbs slug={slug} />

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_250px] gap-8">
        {/* Main Content */}
        <div className="min-w-0">
          {/* Document Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-4">{doc.title}</h1>

            {doc.description && (
              <p className="text-lg text-muted-foreground mb-4">
                {doc.description}
              </p>
            )}

            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-4">
              {doc.category && (
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  <span className="capitalize">{doc.category}</span>
                </div>
              )}
              {doc.lastModified && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>{new Date(doc.lastModified).toLocaleDateString()}</span>
                </div>
              )}
            </div>

            {doc.tags && doc.tags.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <Tag className="w-4 h-4 text-muted-foreground" />
                {doc.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs px-2 py-1 bg-primary/10 text-primary rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Markdown Content */}
          <div className="markdown-content">
            <MarkdownRenderer content={doc.content} />
          </div>

          {/* Navigation Footer */}
          <div className="mt-12 pt-8 border-t">
            <div className="flex justify-between items-center">
              {doc.previousDoc ? (
                <a
                  href={`/docs/${doc.previousDoc.slug}`}
                  className="flex items-center gap-2 text-primary hover:underline"
                >
                  <span>←</span>
                  <span>{doc.previousDoc.title}</span>
                </a>
              ) : (
                <div />
              )}
              {doc.nextDoc ? (
                <a
                  href={`/docs/${doc.nextDoc.slug}`}
                  className="flex items-center gap-2 text-primary hover:underline"
                >
                  <span>{doc.nextDoc.title}</span>
                  <span>→</span>
                </a>
              ) : (
                <div />
              )}
            </div>
          </div>
        </div>

        {/* Table of Contents Sidebar */}
        <div className="hidden lg:block">
          <div className="sticky top-8">
            <TableOfContents content={doc.content} />
          </div>
        </div>
      </div>
    </div>
  )
}
