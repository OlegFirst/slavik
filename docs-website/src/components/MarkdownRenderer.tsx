'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkToc from 'remark-toc'
import rehypeHighlight from 'rehype-highlight'
import rehypeSlug from 'rehype-slug'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'
import 'highlight.js/styles/github-dark.css'

interface MarkdownRendererProps {
  content: string
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkToc]}
      rehypePlugins={[
        rehypeHighlight,
        rehypeSlug,
        [rehypeAutolinkHeadings, { behavior: 'wrap' }],
      ]}
      components={{
        // Custom rendering for code blocks
        code({ className, children, ...props }: any) {
          return (
            <code className={className} {...props}>
              {children}
            </code>
          )
        },
        // Custom rendering for links
        a({ node, children, href, ...props }) {
          const isExternal = href?.startsWith('http')
          return (
            <a
              href={href}
              target={isExternal ? '_blank' : undefined}
              rel={isExternal ? 'noopener noreferrer' : undefined}
              {...props}
            >
              {children}
            </a>
          )
        },
        // Custom rendering for images
        img({ node, src, alt, ...props }) {
          return (
            <img
              src={src}
              alt={alt || ''}
              className="max-w-full h-auto rounded-lg my-4"
              {...props}
            />
          )
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
