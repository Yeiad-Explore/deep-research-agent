"use client"

import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ConfigPanel } from "@/components/research/config-panel"
import { EnhancedProgressTracker } from "@/components/research/enhanced-progress-tracker"
import { DiscoveriesFeed } from "@/components/research/discoveries-feed"
import { ResultsDisplay } from "@/components/research/results-display"
import { ResearchAPI } from "@/lib/api"
import { ResearchConfig, ResearchResponse, ProgressUpdate, Source } from "@/types/research"

interface Discovery {
  id: string
  type: string
  content: string
  timestamp: Date
}

interface ProgressData {
  web_results?: number
  reddit_posts?: number
  scraped_content?: number
}

const api = new ResearchAPI()

export default function Home() {
  const [isResearching, setIsResearching] = useState(false)
  const [currentQuery, setCurrentQuery] = useState("")
  const [results, setResults] = useState<ResearchResponse | null>(null)
  const [currentStage, setCurrentStage] = useState<string | undefined>()
  const [completedStages, setCompletedStages] = useState<Set<string>>(new Set())
  const [discoveries, setDiscoveries] = useState<Discovery[]>([])
  const [error, setError] = useState<string | null>(null)
  const [progressData, setProgressData] = useState<ProgressData>({})
  const [sources, setSources] = useState<Source[]>([])

  const stageMap: Record<string, string> = {
    query_planner: "planning",
    multi_source_searcher: "searching",
    content_scraper: "scraping",
    answer_generator: "answering",
  }

  const handleStartResearch = useCallback(async (query: string, config: ResearchConfig) => {
    setIsResearching(true)
    setCurrentQuery(query)
    setResults(null)
    setCurrentStage(undefined)
    setCompletedStages(new Set())
    setDiscoveries([])
    setError(null)
    setProgressData({})
    setSources([])

    const newDiscoveries: Discovery[] = []

    try {
      const result = await api.startResearchStream(query, config, (update: ProgressUpdate) => {
        // Handle progress updates
        if (update.status === "started") {
          newDiscoveries.push({
            id: Date.now().toString(),
            type: "System",
            content: `Research started: ${update.query}`,
            timestamp: new Date(),
          })
          setDiscoveries([...newDiscoveries])
        } else if (update.status === "in_progress") {
          const stageId = update.stage ? stageMap[update.stage] || update.stage : undefined
          if (stageId) {
            setCurrentStage(stageId)
          }

          if (update.message) {
            newDiscoveries.push({
              id: Date.now().toString(),
              type: "Progress",
              content: update.message,
              timestamp: new Date(),
            })
            setDiscoveries([...newDiscoveries])
          }

          // Update progress data
          if (update.data) {
            setProgressData((prev) => ({
              ...prev,
              ...update.data,
            }))

            if (update.data.web_results && update.data.web_results > 0) {
              newDiscoveries.push({
                id: Date.now().toString(),
                type: "Web",
                content: `Found ${update.data.web_results} web results`,
                timestamp: new Date(),
              })
              setDiscoveries([...newDiscoveries])
            }
            if (update.data.reddit_posts && update.data.reddit_posts > 0) {
              newDiscoveries.push({
                id: Date.now().toString(),
                type: "Reddit",
                content: `Found ${update.data.reddit_posts} Reddit posts`,
                timestamp: new Date(),
              })
              setDiscoveries([...newDiscoveries])
            }
          }

          // Update sources from the state if available
          if (update.result?.sources) {
            setSources(update.result.sources)
          }

          // Mark previous stages as completed
          if (update.stage) {
            const currentStageId = stageMap[update.stage] || update.stage
            const stageOrder = ["planning", "searching", "scraping", "analyzing", "validation", "synthesis"]
            const currentIndex = stageOrder.indexOf(currentStageId)

            if (currentIndex >= 0) {
              setCompletedStages((prev) => {
                const newSet = new Set(prev)
                for (let i = 0; i < currentIndex; i++) {
                  newSet.add(stageOrder[i])
                }
                return newSet
              })
            }
          }
        } else if (update.status === "complete") {
          newDiscoveries.push({
            id: Date.now().toString(),
            type: "System",
            content: "Research completed successfully!",
            timestamp: new Date(),
          })
          setDiscoveries([...newDiscoveries])

          // Mark all stages as completed
          setCompletedStages(new Set(Object.values(stageMap)))
          setCurrentStage(undefined)

          // Update final sources
          if (update.result?.sources) {
            setSources(update.result.sources)
          }
        } else if (update.status === "error") {
          setError(update.message || "An error occurred during research")
        }
      })

      setResults(result)
      setIsResearching(false)
    } catch (err) {
      console.error("Research error:", err)
      setError(err instanceof Error ? err.message : "An error occurred during research")
      setIsResearching(false)
    }
  }, [])

  const handleRefine = useCallback(async (refinementQuery: string) => {
    if (!api.currentSessionId) {
      setError("No active research session to refine")
      return
    }

    setIsResearching(true)
    setError(null)

    try {
      const result = await api.refineResearch(api.currentSessionId, refinementQuery)
      setResults(result)

      setDiscoveries((prev) => [
        {
          id: Date.now().toString(),
          type: "System",
          content: "Research refined successfully!",
          timestamp: new Date(),
        },
        ...prev,
      ])
      setIsResearching(false)
    } catch (err) {
      console.error("Refinement error:", err)
      setError(err instanceof Error ? err.message : "Error refining research")
      setIsResearching(false)
    }
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Deep Research Agent
          </h1>
          <p className="text-muted-foreground text-lg">
            AI-Powered Deep Research with Web & Reddit Community Insights
          </p>
        </motion.div>

        {/* Configuration Panel */}
        <div className="mb-8">
          <ConfigPanel onStartResearch={handleStartResearch} isResearching={isResearching} />
        </div>

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6 p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-200"
            >
              <strong>Error:</strong> {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Enhanced Progress Tracker */}
        <AnimatePresence>
          {(isResearching || results) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <EnhancedProgressTracker
                currentStage={currentStage}
                completedStages={completedStages}
                progressData={progressData}
                sources={sources}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Discoveries Feed - Only shown during research */}
        <AnimatePresence>
          {isResearching && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <DiscoveriesFeed discoveries={discoveries} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Display */}
        <AnimatePresence>
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
            >
              <ResultsDisplay
                data={results}
                query={currentQuery}
                onRefine={handleRefine}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center text-muted-foreground text-sm"
        >
          <p>Powered by LangGraph, Tavily AI, YARS, and Azure OpenAI</p>
        </motion.footer>
      </div>
    </main>
  )
}
