"use client"

import { Lightbulb, TrendingUp, TrendingDown, AlertTriangle, Target } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Insight {
  id: string
  type: "opportunity" | "warning" | "trend" | "action"
  title: string
  description: string
  metric?: string
  priority: "high" | "medium" | "low"
}

interface AIInsightsCardProps {
  insights?: Insight[]
}

// Mock insights for demonstration
const mockInsights: Insight[] = [
  {
    id: "1",
    type: "trend",
    title: "Positive sentiment up 23%",
    description: "Your product mentions have become significantly more positive over the last 2 weeks, especially on r/SaaS.",
    metric: "+23%",
    priority: "high",
  },
  {
    id: "2",
    type: "opportunity",
    title: "Dark mode frequently requested",
    description: "12 users mentioned wanting dark mode this month. Consider adding it to your roadmap.",
    metric: "12 mentions",
    priority: "medium",
  },
  {
    id: "3",
    type: "warning",
    title: "Pricing concerns emerging",
    description: "5 negative mentions about pricing in the last week. Users comparing to cheaper alternatives.",
    metric: "5 mentions",
    priority: "high",
  },
  {
    id: "4",
    type: "action",
    title: "r/startups has high engagement",
    description: "Your posts on r/startups get 3x more engagement than other subreddits. Double down there.",
    metric: "3x engagement",
    priority: "medium",
  },
]

const typeIcons = {
  opportunity: Target,
  warning: AlertTriangle,
  trend: TrendingUp,
  action: Lightbulb,
}

const typeColors = {
  opportunity: "text-blue-500",
  warning: "text-amber-500",
  trend: "text-green-500",
  action: "text-purple-500",
}

const priorityColors = {
  high: "destructive",
  medium: "secondary",
  low: "outline",
} as const

export function AIInsightsCard({ insights = mockInsights }: AIInsightsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5" />
          AI Insights
        </CardTitle>
        <CardDescription>Automated analysis and recommendations</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {insights.map((insight) => {
          const Icon = typeIcons[insight.type]
          return (
            <div
              key={insight.id}
              className="flex gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <div className={`mt-0.5 ${typeColors[insight.type]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium text-sm">{insight.title}</p>
                  <Badge variant={priorityColors[insight.priority]} className="text-xs">
                    {insight.priority}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{insight.description}</p>
                {insight.metric && (
                  <p className="text-xs font-medium text-primary">{insight.metric}</p>
                )}
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
