"use client"

import { memo } from "react"
import { motion } from "framer-motion"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { Card } from "@/components/ui/card"
import { 
  Sparkles
} from "lucide-react"

interface FormattedSynthesisProps {
  synthesis: string
}

// Enhanced markdown components with better hierarchy and spacing
const markdownComponents = {
  h1: ({ children }: any) => (
    <motion.h1 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-3xl font-bold mt-8 mb-6 text-foreground border-b-2 border-primary/20 pb-3"
    >
      {children}
    </motion.h1>
  ),
  h2: ({ children }: any) => (
    <motion.h2 
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 }}
      className="text-2xl font-semibold mt-10 mb-4 text-foreground flex items-center gap-2 pt-2"
    >
      <Sparkles className="h-5 w-5 text-primary/70" />
      {children}
    </motion.h2>
  ),
  h3: ({ children }: any) => (
    <h3 className="text-xl font-semibold mt-8 mb-3 text-foreground text-primary/90">
      {children}
    </h3>
  ),
  h4: ({ children }: any) => (
    <h4 className="text-lg font-semibold mt-6 mb-2 text-foreground">
      {children}
    </h4>
  ),
  p: ({ children }: any) => {
    // Handle React elements or strings
    const getTextContent = (node: any): string => {
      if (typeof node === 'string') return node
      if (Array.isArray(node)) return node.map(getTextContent).join('')
      if (node?.props?.children) return getTextContent(node.props.children)
      return String(node || '')
    }
    
    const text = getTextContent(children)
    
    // Split long paragraphs into shorter ones (2-4 lines max)
    if (text.length > 200) {
      const sentences = text.match(/[^.!?]+[.!?]+/g) || [text]
      const chunks: string[] = []
      let currentChunk = ''
      
      sentences.forEach(sentence => {
        const testChunk = currentChunk + sentence
        // Keep chunks to ~180 chars for 2-4 line paragraphs
        if (testChunk.length < 180) {
          currentChunk = testChunk
        } else {
          if (currentChunk.trim()) chunks.push(currentChunk.trim())
          currentChunk = sentence
        }
      })
      if (currentChunk.trim()) chunks.push(currentChunk.trim())
      
      // If we have multiple chunks, render them separately with spacing
      if (chunks.length > 1) {
        return (
          <div className="space-y-4">
            {chunks.map((chunk, i) => (
              <p key={i} className="text-foreground leading-7 text-base">
                {chunk}
              </p>
            ))}
          </div>
        )
      }
    }
    return (
      <p className="mb-5 text-foreground leading-7 text-base">
        {children}
      </p>
    )
  },
  ul: ({ children }: any) => (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="my-8"
    >
      <Card className="border-l-4 border-l-primary/50 bg-muted/30 shadow-sm">
        <ul className="p-6 space-y-4 text-foreground list-none">
          {children}
        </ul>
      </Card>
    </motion.div>
  ),
  ol: ({ children }: any) => (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="my-8"
    >
      <Card className="border-l-4 border-l-primary/50 bg-muted/30 shadow-sm">
        <ol className="p-6 space-y-4 text-foreground list-decimal list-inside ml-2">
          {children}
        </ol>
      </Card>
    </motion.div>
  ),
  li: ({ children }: any) => (
    <li className="text-base leading-7 text-foreground pl-4 relative before:content-['•'] before:absolute before:left-0 before:text-primary before:font-bold before:text-xl">
      {children}
    </li>
  ),
  strong: ({ children }: any) => (
    <strong className="font-semibold text-foreground bg-primary/10 px-1.5 py-0.5 rounded">
      {children}
    </strong>
  ),
  em: ({ children }: any) => (
    <em className="italic text-foreground text-primary/90">{children}</em>
  ),
  blockquote: ({ children }: any) => (
    <motion.blockquote 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="border-l-4 border-primary/60 pl-6 py-4 my-6 italic bg-gradient-to-r from-primary/5 to-transparent rounded-r-lg"
    >
      <div className="text-foreground/90 leading-7">{children}</div>
    </motion.blockquote>
  ),
  code: ({ children }: any) => (
    <code className="bg-muted px-2 py-1 rounded text-sm font-mono border border-border">
      {children}
    </code>
  ),
  a: ({ href, children }: any) => (
    <a 
      href={href} 
      target="_blank" 
      rel="noopener noreferrer"
      className="text-primary hover:underline font-medium underline-offset-2"
    >
      {children}
    </a>
  ),
  hr: () => (
    <div className="my-8 border-t border-border/50" />
  ),
}

function formatSynthesisText(text: string): string {
  if (!text) return ""
  
  let formatted = text
  
  // Remove [Source X] patterns and integrate naturally if possible
  formatted = formatted.replace(/\[Source\s+\d+\]/gi, '')
  formatted = formatted.replace(/\[Source:\s*\d+\]/gi, '')
  formatted = formatted.replace(/\(Source\s+\d+\)/gi, '')
  formatted = formatted.replace(/\[Source\d+\]/gi, '')
  formatted = formatted.replace(/\[Sources?\s*\d+[\s-]?\d*\]/gi, '')
  formatted = formatted.replace(/\[Sources?[^\]]*\]/gi, '')
  
  // Clean up excessive whitespace
  formatted = formatted.replace(/\n{3,}/g, '\n\n')
  formatted = formatted.replace(/[ \t]+/g, ' ')
  formatted = formatted.replace(/\s+$/gm, '') // Remove trailing whitespace on lines
  
  // Ensure proper spacing around headings
  formatted = formatted.replace(/\n(#+)\s*/g, '\n\n\n$1 ')
  formatted = formatted.replace(/(#+[^\n]+)\n([^\n#])/g, '$1\n\n$2')
  
  return formatted.trim()
}

export const FormattedSynthesis = memo(function FormattedSynthesis({
  synthesis,
}: FormattedSynthesisProps) {
  const formattedText = formatSynthesisText(synthesis)
  
  return (
    <div className="space-y-8">
      {/* Main Content with Better Spacing */}
      <div className="max-w-none text-foreground">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {formattedText || "No response available. The research may still be processing."}
        </ReactMarkdown>
      </div>
    </div>
  )
})
