"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bell, ExternalLink } from "lucide-react"

interface Discovery {
  id: string
  type: string
  content: string
  timestamp: Date
}

interface DiscoveriesFeedProps {
  discoveries: Discovery[]
}

export function DiscoveriesFeed({ discoveries }: DiscoveriesFeedProps) {
  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "web":
        return "bg-blue-600"
      case "reddit":
        return "bg-orange-600"
      case "system":
        return "bg-purple-600"
      case "progress":
        return "bg-green-600"
      case "error":
        return "bg-red-600"
      default:
        return "bg-gray-600"
    }
  }

  return (
    <Card className="max-h-[400px] flex flex-col">
      <CardHeader className="flex-shrink-0">
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Live Discoveries
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto">
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {discoveries.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-muted-foreground py-8"
              >
                No discoveries yet. Start researching to see live updates!
              </motion.div>
            ) : (
              discoveries.map((discovery, index) => (
                <motion.div
                  key={discovery.id}
                  initial={{ opacity: 0, x: -20, scale: 0.95 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: 20, scale: 0.95 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-3 rounded-lg bg-muted/50 border-l-4 border-l-primary"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={getTypeColor(discovery.type)}>
                          {discovery.type}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {discovery.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm">{discovery.content}</p>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  )
}
