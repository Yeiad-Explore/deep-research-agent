"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Brain,
  Search,
  Download,
  FileText,
  CheckCircle2,
  Loader2,
  Circle,
  Globe,
  MessageCircle,
  MessageSquare,
  TrendingUp,
} from "lucide-react"
import { useEffect, useState } from "react"

interface Stage {
  id: string
  label: string
  icon: React.ReactNode
  nodeName: string
  description: string
  color: {
    active: string
    completed: string
    pending: string
    gradient: string
  }
}

const stages: Stage[] = [
  {
    id: "planning",
    label: "Query Planning",
    icon: <Brain className="h-6 w-6" />,
    nodeName: "query_planner",
    description: "Analyzing query & creating strategy",
    color: {
      active: "from-blue-500 to-cyan-500",
      completed: "from-green-500 to-emerald-500",
      pending: "from-gray-400 to-gray-500",
      gradient: "from-blue-500/20 via-cyan-500/20 to-blue-500/20",
    },
  },
  {
    id: "searching",
    label: "Multi-Source Search",
    icon: <Search className="h-6 w-6" />,
    nodeName: "multi_source_searcher",
    description: "Web search",
    color: {
      active: "from-purple-500 to-pink-500",
      completed: "from-green-500 to-emerald-500",
      pending: "from-gray-400 to-gray-500",
      gradient: "from-purple-500/20 via-pink-500/20 to-purple-500/20",
    },
  },
  {
    id: "scraping",
    label: "Content Gathering",
    icon: <Download className="h-6 w-6" />,
    nodeName: "content_scraper",
    description: "Scraping URLs & threads",
    color: {
      active: "from-indigo-500 to-purple-500",
      completed: "from-green-500 to-emerald-500",
      pending: "from-gray-400 to-gray-500",
      gradient: "from-indigo-500/20 via-purple-500/20 to-indigo-500/20",
    },
  },
  {
    id: "answering",
    label: "Generating Answer",
    icon: <FileText className="h-6 w-6" />,
    nodeName: "answer_generator",
    description: "Creating AI response",
    color: {
      active: "from-emerald-500 to-green-500",
      completed: "from-green-500 to-emerald-500",
      pending: "from-gray-400 to-gray-500",
      gradient: "from-emerald-500/20 via-green-500/20 to-emerald-500/20",
    },
  },
]

const stageMap: Record<string, string> = {
  query_planner: "planning",
  multi_source_searcher: "searching",
  content_scraper: "scraping",
  answer_generator: "answering",
}

interface ProgressData {
  web_results?: number
  scraped_content?: number
}

interface EnhancedProgressTrackerProps {
  currentStage?: string
  completedStages: Set<string>
  progressData?: ProgressData
  sources?: Array<{ title: string; url: string; type?: "web" }>
}

interface Particle {
  id: string
  fromStage: number
  toStage: number
  progress: number
  type: "web"
}

export function EnhancedProgressTracker({
  currentStage,
  completedStages,
  progressData = {},
  sources = [],
}: EnhancedProgressTrackerProps) {
  const [particles, setParticles] = useState<Particle[]>([])
  const [hoveredStage, setHoveredStage] = useState<string | null>(null)

  const getStageStatus = (stageId: string) => {
    if (completedStages.has(stageId)) return "completed"
    const stageIndex = stages.findIndex((s) => s.id === stageId)
    const currentIndex = currentStage ? stages.findIndex((s) => s.id === currentStage) : -1

    if (currentIndex >= 0 && stageIndex < currentIndex) {
      return "completed"
    }

    if (currentStage === stageId) return "in_progress"
    return "pending"
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
          >
            <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
          </motion.div>
        )
      case "in_progress":
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Loader2 className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          </motion.div>
        )
      default:
        return <Circle className="h-6 w-6 text-gray-400" />
    }
  }

  const getParallelIndicators = (stageId: string) => {
    if (stageId === "searching" && getStageStatus(stageId) === "in_progress") {
      return (
        <div className="mt-2 space-y-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            className="flex items-center gap-2 text-xs"
          >
            <Globe className="h-3 w-3 text-blue-500" />
            <span className="text-blue-600 dark:text-blue-400">Web Search</span>
            {progressData.web_results !== undefined && (
              <Badge variant="secondary" className="ml-auto animate-pulse">
                {progressData.web_results}
              </Badge>
            )}
          </motion.div>
        </div>
      )
    }

    if (stageId === "analyzing" && getStageStatus(stageId) === "in_progress") {
      return (
        <div className="mt-2 space-y-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            className="flex items-center gap-2 text-xs"
          >
            <TrendingUp className="h-3 w-3 text-teal-500" />
            <span className="text-teal-600 dark:text-teal-400">Web Summaries</span>
            {progressData.web_summaries !== undefined && (
              <Badge variant="secondary" className="ml-auto animate-pulse">
                {progressData.web_summaries}
              </Badge>
            )}
          </motion.div>
        </div>
      )
    }

    if (stageId === "validation" && getStageStatus(stageId) === "in_progress") {
      return (
        <div className="mt-2 space-y-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            className="flex items-center gap-2 text-xs"
          >
            <CheckCircle2 className="h-3 w-3 text-green-500" />
            <span className="text-green-600 dark:text-green-400">Corroborated Facts</span>
            {progressData.corroborated_facts !== undefined && (
              <Badge variant="secondary" className="ml-auto animate-pulse">
                {progressData.corroborated_facts}
              </Badge>
            )}
          </motion.div>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-2 text-xs"
          >
            <FileCheck className="h-3 w-3 text-amber-500" />
            <span className="text-amber-600 dark:text-amber-400">Expert Opinions</span>
            {progressData.expert_opinions !== undefined && (
              <Badge variant="secondary" className="ml-auto animate-pulse">
                {progressData.expert_opinions}
              </Badge>
            )}
          </motion.div>
        </div>
      )
    }

    return null
  }

  // Spawn particles when stage changes
  useEffect(() => {
    if (!currentStage) return

    const currentIndex = stages.findIndex((s) => s.id === currentStage)
    if (currentIndex <= 0) return

    // Create particles flowing from previous stage to current
    const newParticles: Particle[] = []
    for (let i = 0; i < 3; i++) {
      newParticles.push({
        id: `${Date.now()}-${i}`,
        fromStage: currentIndex - 1,
        toStage: currentIndex,
        progress: 0,
        type: "web",
      })
    }

    setParticles((prev) => [...prev, ...newParticles])

    // Animate particles
    const interval = setInterval(() => {
      setParticles((prev) =>
        prev
          .map((p) => ({ ...p, progress: p.progress + 0.02 }))
          .filter((p) => p.progress < 1)
      )
    }, 50)

    return () => clearInterval(interval)
  }, [currentStage])

  const currentStageId = currentStage ? stageMap[currentStage] || currentStage : undefined
  const currentStageIndex = currentStageId ? stages.findIndex((s) => s.id === currentStageId) : -1

  // Background gradient based on current stage
  const backgroundGradient =
    currentStageIndex >= 0
      ? stages[currentStageIndex].color.gradient
      : "from-gray-500/10 via-gray-500/10 to-gray-500/10"

  return (
    <motion.div
      className={`relative p-6 rounded-xl bg-gradient-to-br ${backgroundGradient} backdrop-blur-sm transition-all duration-1000`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Iteration Counter */}
      {progressData.iteration !== undefined && progressData.iteration > 0 && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute top-4 right-4 flex items-center gap-2"
        >
          <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2">
            <span className="text-sm font-semibold">
              Iteration {progressData.iteration + 1}
            </span>
          </Badge>
        </motion.div>
      )}

      <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: [0, 5, 0, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Brain className="h-6 w-6 text-blue-600" />
            </motion.div>
            Research Pipeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Pipeline Visualization */}
          <div className="relative">
            {/* Connecting Lines with Particles */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" style={{ height: "calc(100% + 20px)" }}>
              {stages.map((stage, index) => {
                if (index === stages.length - 1) return null
                const fromX = `${(index / (stages.length - 1)) * 100}%`
                const toX = `${((index + 1) / (stages.length - 1)) * 100}%`
                const status = getStageStatus(stage.id)

                return (
                  <motion.line
                    key={`line-${index}`}
                    x1={fromX}
                    y1="50%"
                    x2={toX}
                    y2="50%"
                    stroke={status === "completed" ? "#10b981" : "#e5e7eb"}
                    strokeWidth="3"
                    strokeDasharray={status === "in_progress" ? "5,5" : "0"}
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: status === "completed" ? 1 : status === "in_progress" ? 0.5 : 0 }}
                    transition={{ duration: 0.5 }}
                  />
                )
              })}

              {/* Animated Particles */}
              {particles.map((particle) => {
                const fromX = (particle.fromStage / (stages.length - 1)) * 100
                const toX = (particle.toStage / (stages.length - 1)) * 100
                const x = fromX + (toX - fromX) * particle.progress

                return (
                  <motion.circle
                    key={particle.id}
                    cx={`${x}%`}
                    cy="50%"
                    r="4"
                    fill="#3b82f6"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 1, 1, 0] }}
                    transition={{ duration: 2 }}
                  />
                )
              })}
            </svg>

            {/* Stage Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 relative z-10">
              {stages.map((stage, index) => {
                const status = getStageStatus(stage.id)
                const isActive = status === "in_progress"
                const isHovered = hoveredStage === stage.id

                return (
                  <motion.div
                    key={stage.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onHoverStart={() => setHoveredStage(stage.id)}
                    onHoverEnd={() => setHoveredStage(null)}
                  >
                    <motion.div
                      className={`relative p-4 rounded-xl border-2 transition-all duration-300 ${
                        isActive
                          ? "border-transparent shadow-2xl scale-105"
                          : status === "completed"
                          ? "border-green-500 bg-green-50/50 dark:bg-green-950/50"
                          : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
                      }`}
                      animate={
                        isActive
                          ? {
                              scale: isHovered ? 1.08 : 1.05,
                              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                            }
                          : { scale: isHovered ? 1.02 : 1 }
                      }
                      style={{
                        background: isActive
                          ? `linear-gradient(135deg, ${stage.color.active.includes("from") ? "var(--tw-gradient-from), var(--tw-gradient-to)" : stage.color.active})`
                          : undefined,
                      }}
                    >
                      {/* Pulsing Background for Active Stage */}
                      {isActive && (
                        <motion.div
                          className={`absolute inset-0 rounded-xl bg-gradient-to-br ${stage.color.active} opacity-20`}
                          animate={{ opacity: [0.2, 0.4, 0.2] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        />
                      )}

                      <div className="relative z-10">
                        {/* Icon and Status */}
                        <div className="flex items-center justify-between mb-3">
                          <motion.div
                            className={`p-2 rounded-lg ${
                              isActive
                                ? "bg-white/90 dark:bg-gray-900/90 text-blue-600"
                                : status === "completed"
                                ? "bg-green-100 dark:bg-green-900 text-green-600"
                                : "bg-gray-100 dark:bg-gray-700 text-gray-500"
                            }`}
                            animate={isActive ? { rotate: [0, 5, 0, -5, 0] } : {}}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            {stage.icon}
                          </motion.div>
                          {getStatusIcon(status)}
                        </div>

                        {/* Label */}
                        <h4
                          className={`font-semibold text-sm mb-1 ${
                            isActive ? "text-white" : "text-gray-900 dark:text-gray-100"
                          }`}
                        >
                          {stage.label}
                        </h4>

                        {/* Description */}
                        <p
                          className={`text-xs ${
                            isActive
                              ? "text-white/80"
                              : "text-gray-600 dark:text-gray-400"
                          }`}
                        >
                          {stage.description}
                        </p>

                        {/* Parallel Process Indicators */}
                        <AnimatePresence>
                          {isActive && getParallelIndicators(stage.id)}
                        </AnimatePresence>

                        {/* Progress Badge */}
                        {isActive && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-3"
                          >
                            <Badge className="bg-white/90 dark:bg-gray-900/90 text-blue-600 animate-pulse w-full justify-center">
                              Processing...
                            </Badge>
                          </motion.div>
                        )}

                        {status === "completed" && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="mt-3"
                          >
                            <Badge className="bg-green-600 text-white w-full justify-center">
                              ✓ Complete
                            </Badge>
                          </motion.div>
                        )}
                      </div>
                    </motion.div>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {/* Source Preview Cards */}
          {sources.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <h3 className="text-sm font-semibold mb-3 text-gray-700 dark:text-gray-300">
                Sources Discovered ({sources.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto">
                {sources.slice(0, 9).map((source, index) => (
                  <motion.a
                    key={`${source.url}-${index}`}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="group flex items-start gap-2 p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md hover:border-blue-400 transition-all"
                  >
                    <div
                      className={`mt-0.5 ${
                        source.type === "web" ? "text-blue-500" : "text-orange-500"
                      }`}
                    >
                      {source.type === "web" ? (
                        <Globe className="h-4 w-4" />
                      ) : (
                        <MessageCircle className="h-4 w-4" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 dark:text-gray-100 truncate group-hover:text-blue-600 transition-colors">
                        {source.title}
                      </p>
                      <Badge
                        variant="secondary"
                        className="mt-1 text-xs"
                      >
                        Web
                      </Badge>
                    </div>
                  </motion.a>
                ))}
              </div>
              {sources.length > 9 && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                  +{sources.length - 9} more sources
                </p>
              )}
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
