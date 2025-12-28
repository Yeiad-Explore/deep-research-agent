"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Brain,
  Search,
  Download,
  Microscope,
  MessageSquare,
  FileText,
  CheckCircle2,
  Loader2,
  Circle,
} from "lucide-react"

interface Stage {
  id: string
  label: string
  icon: React.ReactNode
  nodeName: string
}

const stages: Stage[] = [
  {
    id: "planning",
    label: "Planning Research",
    icon: <Brain className="h-6 w-6" />,
    nodeName: "query_planner",
  },
  {
    id: "searching",
    label: "Searching Web & Reddit",
    icon: <Search className="h-6 w-6" />,
    nodeName: "multi_source_searcher",
  },
  {
    id: "scraping",
    label: "Gathering Content",
    icon: <Download className="h-6 w-6" />,
    nodeName: "content_scraper",
  },
  {
    id: "analyzing",
    label: "Analyzing Sources",
    icon: <Microscope className="h-6 w-6" />,
    nodeName: "content_analyzer",
  },
  {
    id: "consensus",
    label: "Building Consensus",
    icon: <MessageSquare className="h-6 w-6" />,
    nodeName: "consensus_builder",
  },
  {
    id: "synthesis",
    label: "Synthesizing Report",
    icon: <FileText className="h-6 w-6" />,
    nodeName: "synthesis",
  },
]

const stageMap: Record<string, string> = {
  query_planner: "planning",
  multi_source_searcher: "searching",
  content_scraper: "scraping",
  content_analyzer: "analyzing",
  consensus_builder: "consensus",
  cross_reference: "analyzing",
  synthesis: "synthesis",
  quality_checker: "synthesis",
  gap_filler: "searching",
}

interface ProgressTrackerProps {
  currentStage?: string
  completedStages: Set<string>
}

export function ProgressTracker({ currentStage, completedStages }: ProgressTrackerProps) {
  const getStageStatus = (stageId: string) => {
    if (completedStages.has(stageId)) return "completed"
    const stageIndex = stages.findIndex((s) => s.id === stageId)
    const currentIndex = currentStage ? stages.findIndex((s) => s.id === currentStage) : -1
    
    // If current stage is active, mark previous stages as completed
    if (currentIndex >= 0 && stageIndex < currentIndex) {
      return "completed"
    }
    
    if (currentStage === stageId) return "in_progress"
    return "pending"
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-600" />
      case "in_progress":
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <Loader2 className="h-5 w-5 text-blue-600" />
          </motion.div>
        )
      default:
        return <Circle className="h-5 w-5 text-muted-foreground" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-600">Completed</Badge>
      case "in_progress":
        return <Badge className="bg-blue-600 animate-pulse">In Progress</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  const currentStageId = currentStage ? stageMap[currentStage] || currentStage : undefined

  return (
    <Card>
      <CardHeader>
        <CardTitle>Research Progress</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stages.map((stage, index) => {
            const status = getStageStatus(stage.id)
            const isActive = status === "in_progress"

            return (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <motion.div
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isActive
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-950 shadow-lg scale-105"
                      : status === "completed"
                      ? "border-green-500 bg-green-50 dark:bg-green-950"
                      : "border-muted bg-muted/30"
                  }`}
                  animate={isActive ? { scale: 1.05 } : { scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`p-2 rounded-lg ${
                          isActive
                            ? "bg-blue-100 dark:bg-blue-900 text-blue-600"
                            : status === "completed"
                            ? "bg-green-100 dark:bg-green-900 text-green-600"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {stage.icon}
                      </div>
                      <div>
                        <h4 className="font-semibold text-sm">{stage.label}</h4>
                      </div>
                    </div>
                    {getStatusIcon(status)}
                  </div>
                  <div className="flex justify-end">{getStatusBadge(status)}</div>
                </motion.div>
              </motion.div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
