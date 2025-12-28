"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronDown, ChevronUp, Settings, Sparkles } from "lucide-react"
import { ResearchConfig } from "@/types/research"

interface ConfigPanelProps {
  onStartResearch: (query: string, config: ResearchConfig) => void
  isResearching: boolean
}

export function ConfigPanel({ onStartResearch, isResearching }: ConfigPanelProps) {
  const [query, setQuery] = useState("")
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [config, setConfig] = useState<ResearchConfig>({
    depth: "standard",
    include_reddit: true,
    time_filter: "month",
    max_web_results: 15,
    max_reddit_posts: 50,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onStartResearch(query.trim(), config)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="border-2 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="h-6 w-6" />
            Deep Research Agent
          </CardTitle>
          <CardDescription className="text-white/90">
            AI-Powered Research with Web & Reddit Community Insights
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="query" className="text-base font-semibold">
                Research Question
              </Label>
              <Input
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., What are developers saying about Python 3.13?"
                className="h-12 text-base"
                disabled={isResearching}
              />
            </div>

            <motion.div
              initial={false}
              animate={{ height: showAdvanced ? "auto" : 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full flex items-center justify-between"
              >
                <span className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Advanced Options
                </span>
                {showAdvanced ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>

              <AnimatePresence>
                {showAdvanced && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="mt-4 space-y-4 p-4 bg-muted/50 rounded-lg"
                  >
                    <div className="space-y-2">
                      <Label htmlFor="depth">Research Depth</Label>
                      <Select
                        value={config.depth}
                        onValueChange={(value: "quick" | "standard" | "comprehensive") =>
                          setConfig({ ...config, depth: value })
                        }
                      >
                        <SelectTrigger id="depth">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="quick">Quick (1-2 iterations)</SelectItem>
                          <SelectItem value="standard">Standard (2-3 iterations)</SelectItem>
                          <SelectItem value="comprehensive">Comprehensive (3-5 iterations)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="include-reddit"
                        checked={config.include_reddit}
                        onCheckedChange={(checked) =>
                          setConfig({ ...config, include_reddit: checked as boolean })
                        }
                      />
                      <Label htmlFor="include-reddit" className="cursor-pointer">
                        Include Reddit Discussions
                      </Label>
                    </div>

                    {config.include_reddit && (
                      <>
                        <div className="space-y-2">
                          <Label htmlFor="subreddits">Specific Subreddits (optional)</Label>
                          <Input
                            id="subreddits"
                            placeholder="e.g., python,programming,learnpython"
                            onChange={(e) => {
                              const subreddits = e.target.value
                                ? e.target.value.split(",").map((s) => s.trim())
                                : null
                              setConfig({ ...config, subreddits })
                            }}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="time-filter">Reddit Time Filter</Label>
                          <Select
                            value={config.time_filter}
                            onValueChange={(value) =>
                              setConfig({ ...config, time_filter: value })
                            }
                          >
                            <SelectTrigger id="time-filter">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="day">Past 24 Hours</SelectItem>
                              <SelectItem value="week">Past Week</SelectItem>
                              <SelectItem value="month">Past Month</SelectItem>
                              <SelectItem value="year">Past Year</SelectItem>
                              <SelectItem value="all">All Time</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            <Button
              type="submit"
              size="lg"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold h-12 text-base shadow-lg"
              disabled={isResearching || !query.trim()}
            >
              {isResearching ? (
                <span className="flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="h-5 w-5 border-2 border-white border-t-transparent rounded-full"
                  />
                  Researching...
                </span>
              ) : (
                <>
                  <Sparkles className="h-5 w-5 mr-2" />
                  Start Deep Research
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  )
}
