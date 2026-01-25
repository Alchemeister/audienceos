"use client"

import {
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Users,
  MessageSquare,
  Target,
  Bell,
  Check,
  X,
} from "lucide-react"

import type { Insight } from "@/lib/types"
import { formatRelativeTime, formatPercentage } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface InsightCardProps {
  insight: Insight
  onAction?: (id: string) => void
  onDismiss?: (id: string) => void
}

const typeIcons: Record<string, React.ElementType> = {
  marketing_opportunity: TrendingUp,
  churn_risk: AlertTriangle,
  feature_demand: Lightbulb,
  competitor_insight: Users,
  sentiment_shift: MessageSquare,
  trending_topic: Target,
  action_required: Bell,
}

const priorityVariants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  high: "destructive",
  medium: "default",
  low: "secondary",
}

export function InsightCard({ insight, onAction, onDismiss }: InsightCardProps) {
  const Icon = typeIcons[insight.type] || Lightbulb

  if (insight.is_dismissed) return null

  return (
    <Card className={insight.is_actioned ? "opacity-60" : ""}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">{insight.title}</CardTitle>
              <p className="text-xs text-muted-foreground">
                {formatRelativeTime(insight.created_at)}
              </p>
            </div>
          </div>
          <Badge variant={priorityVariants[insight.priority] || "outline"}>
            {insight.priority}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Description */}
        <p className="text-sm">{insight.description}</p>

        {/* Confidence */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Confidence</span>
          <Progress value={insight.confidence * 100} className="h-1.5 flex-1" />
          <span className="text-xs font-medium">
            {formatPercentage(insight.confidence)}
          </span>
        </div>

        {/* Evidence */}
        {insight.evidence.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Evidence:</p>
            <ul className="text-sm space-y-1">
              {insight.evidence.slice(0, 3).map((evidence, index) => (
                <li key={index} className="text-muted-foreground">
                  • {evidence}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Suggested action */}
        {insight.suggested_action && (
          <div className="bg-muted/50 rounded-md p-3">
            <p className="text-xs text-muted-foreground mb-1">Suggested action:</p>
            <p className="text-sm font-medium">{insight.suggested_action}</p>
          </div>
        )}

        {/* Actions */}
        {!insight.is_actioned && (onAction || onDismiss) && (
          <div className="flex items-center gap-2 pt-2 border-t">
            {onAction && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onAction(insight.id)}
              >
                <Check className="mr-1 h-3 w-3" />
                Mark as Actioned
              </Button>
            )}
            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDismiss(insight.id)}
              >
                <X className="mr-1 h-3 w-3" />
                Dismiss
              </Button>
            )}
          </div>
        )}
        {insight.is_actioned && (
          <div className="flex items-center gap-1 text-xs text-muted-foreground pt-2 border-t">
            <Check className="h-3 w-3" />
            Actioned {insight.actioned_at && formatRelativeTime(insight.actioned_at)}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
