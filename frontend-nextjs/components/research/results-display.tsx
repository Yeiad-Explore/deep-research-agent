"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ResearchResponse } from "@/types/research"
import { FormattedSynthesis } from "./formatted-synthesis"
import {
  FileText,
  BookOpen,
  Download,
  RefreshCw,
  ExternalLink,
} from "lucide-react"

interface ResultsDisplayProps {
  data: ResearchResponse
  query: string
  onRefine: (refinementQuery: string) => void
}

export function ResultsDisplay({ data, query, onRefine }: ResultsDisplayProps) {
  const [refinementQuery, setRefinementQuery] = useState("")

  const exportAsMarkdown = () => {
    let markdown = `# Research Answer\n\n`
    markdown += `**Question:** ${query}\n\n`
    markdown += `**Date:** ${new Date().toLocaleDateString()}\n\n`
    markdown += `---\n\n`
    markdown += `## Answer\n\n`
    markdown += data.response || "No response available"
    markdown += `\n\n---\n\n`
    markdown += `## Sources\n\n`

    ;(data.sources || []).forEach((source, index) => {
      markdown += `${index + 1}. [${source.title}](${source.url})\n`
    })

    const blob = new Blob([markdown], { type: "text/markdown" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = "research-answer.md"
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportAsJson = () => {
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = "research-data.json"
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleRefine = () => {
    if (refinementQuery.trim()) {
      onRefine(refinementQuery.trim())
      setRefinementQuery("")
    }
  }

  const webSources = data.sources?.filter(s => s.type === "web" || !s.type) || []
  const redditSources = data.sources?.filter(s => s.type === "reddit") || []

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Query Summary */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950 border-purple-200 dark:border-purple-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Research Question
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-lg font-medium">{query}</p>
          <div className="flex flex-wrap gap-3">
            <Badge variant="outline" className="text-sm">
              {data.sources?.length || 0} Sources
            </Badge>
            {webSources.length > 0 && (
              <Badge variant="outline" className="text-sm">
                {webSources.length} Web
              </Badge>
            )}
            {redditSources.length > 0 && (
              <Badge variant="outline" className="text-sm">
                {redditSources.length} Reddit
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* AI Response */}
      <Card>
        <CardHeader>
          <CardTitle>Answer</CardTitle>
          <CardDescription>
            AI-generated response based on web and Reddit research
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <FormattedSynthesis 
            synthesis={data.response || "No response available"}
          />
        </CardContent>
      </Card>

      {/* Sources */}
      {data.sources && data.sources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Sources ({data.sources.length})
            </CardTitle>
            <CardDescription>
              References used to generate the answer above
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.sources.map((source, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className={`border-l-4 ${
                    source.type === "reddit" 
                      ? "border-l-orange-500" 
                      : "border-l-blue-500"
                  }`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <CardTitle className="text-base mb-2">
                            [{index + 1}] {source.title}
                          </CardTitle>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-sm text-primary hover:underline"
                          >
                            {source.url}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                        {source.type && (
                          <Badge 
                            variant="outline"
                            className={source.type === "reddit" ? "border-orange-500 text-orange-600" : ""}
                          >
                            {source.type === "reddit" ? "Reddit" : "Web"}
                          </Badge>
                        )}
                      </div>
                    </CardHeader>
                  </Card>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Export & Refine Options */}
      <Card>
        <CardHeader>
          <CardTitle>Export & Refine</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <Button onClick={exportAsMarkdown} variant="outline" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export as Markdown
            </Button>
            <Button onClick={exportAsJson} variant="outline" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export as JSON
            </Button>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={refinementQuery}
              onChange={(e) => setRefinementQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleRefine()}
              placeholder="What aspect would you like to explore further?"
              className="flex-1 px-3 py-2 border rounded-md"
            />
            <Button onClick={handleRefine} className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Refine Research
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
