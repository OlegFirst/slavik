'use client'

import { useEffect, useState } from 'react'

interface TocItem {
  id: string
  title: string
  level: number
}

interface TableOfContentsProps {
  content: string
}

export function TableOfContents({ content }: TableOfContentsProps) {
  const [toc, setToc] = useState<TocItem[]>([])
  const [activeId, setActiveId] = useState<string>('')

  useEffect(() => {
    // Parse headings from markdown content
    const headingRegex = /^#{2,4}\s+(.+)$/gm
    const items: TocItem[] = []
    let match

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[0].indexOf(' ')
      const title = match[1].replace(/[#*`]/g, '').trim()
      const id = title
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')

      items.push({ id, title, level })
    }

    setToc(items)
  }, [content])

  useEffect(() => {
    // Intersection observer to highlight active section
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        })
      },
      { rootMargin: '-100px 0px -80% 0px' }
    )

    toc.forEach((item) => {
      const element = document.getElementById(item.id)
      if (element) {
        observer.observe(element)
      }
    })

    return () => observer.disconnect()
  }, [toc])

  if (toc.length === 0) {
    return null
  }

  return (
    <div className="space-y-2">
      <h4 className="font-semibold text-sm mb-4">On This Page</h4>
      <nav className="space-y-2">
        {toc.map((item) => (
          <a
            key={item.id}
            href={`#${item.id}`}
            className={`block text-sm transition-colors ${
              activeId === item.id
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground'
            }`}
            style={{ paddingLeft: `${(item.level - 2) * 12}px` }}
          >
            {item.title}
          </a>
        ))}
      </nav>
    </div>
  )
}
