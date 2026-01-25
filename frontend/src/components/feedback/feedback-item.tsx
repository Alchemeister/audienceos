"use client"

import { useState } from "react"
import { ExternalLink, Check, AlertTriangle } from "lucide-react"

import type { FeedbackItem as FeedbackItemType } from "@/lib/types"
import {
  formatRelativeTime,
  getSentimentBadgeVariant,
  getUrgencyColor,
  getPlatformLabel,
  getCategoryLabel,
  truncateText,
} from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface FeedbackItemProps {
  item: FeedbackItemType
  onMarkActioned?: (id: string) => void
}

export function FeedbackItem({ item, onMarkActioned }: FeedbackItemProps) {
  const [expanded, setExpanded] = useState(false)
  const isLongText = item.text.length > 200

  return (
    <Card className={item.is_actioned ? "opacity-60" : ""}>
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header row */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline">{getPlatformLabel(item.source)}</Badge>
              <Badge variant={getSentimentBadgeVariant(item.sentiment)}>
                {item.sentiment}
              </Badge>
              <Badge variant="secondary">{getCategoryLabel(item.category)}</Badge>
              {item.urgency === "high" || item.urgency === "critical" ? (
                <Badge className={getUrgencyColor(item.urgency)}>
                  {item.urgency}
                </Badge>
              ) : null}
            </div>
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {formatRelativeTime(item.collected_at)}
            </span>
          </div>

          {/* Author */}
          {item.author && (
            <p className="text-sm text-muted-foreground">
              by <span className="font-medium">{item.author}</span>
            </p>
          )}

          {/* Text content */}
          <p className="text-sm">
            {expanded || !isLongText ? item.text : truncateText(item.text, 200)}
          </p>
          {isLongText && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-primary hover:underline"
            >
              {expanded ? "Show less" : "Show more"}
            </button>
          )}

          {/* Key phrases */}
          {item.key_phrases.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {item.key_phrases.slice(0, 5).map((phrase) => (
                <Badge
                  key={phrase}
                  variant="outline"
                  className="text-xs bg-muted"
                >
                  {phrase}
                </Badge>
              ))}
            </div>
          )}

          {/* Churn risk */}
          {item.churn_risk > 0.3 && (
            <div className="flex items-center gap-2">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-2 flex-1">
                      <AlertTriangle
                        className={`h-4 w-4 ${
                          item.churn_risk > 0.7
                            ? "text-red-500"
                            : item.churn_risk > 0.5
                              ? "text-orange-500"
                              : "text-yellow-500"
                        }`}
                      />
                      <span className="text-xs text-muted-foreground">
                        Churn risk
                      </span>
                      <Progress
                        value={item.churn_risk * 100}
                        className="h-2 flex-1 max-w-[100px]"
                      />
                      <span className="text-xs font-medium">
                        {Math.round(item.churn_risk * 100)}%
                      </span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>AI-estimated churn risk based on sentiment and content</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          )}

          {/* Suggested action */}
          {item.suggested_action && (
            <div className="bg-muted/50 rounded-md p-2">
              <p className="text-xs text-muted-foreground mb-1">
                Suggested action:
              </p>
              <p className="text-sm">{item.suggested_action}</p>
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center gap-2">
              {item.source_url && (
                <a
                  href={item.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
                >
                  <ExternalLink className="h-3 w-3" />
                  View source
                </a>
              )}
            </div>
            {!item.is_actioned && onMarkActioned && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onMarkActioned(item.id)}
              >
                <Check className="mr-1 h-3 w-3" />
                Mark as actioned
              </Button>
            )}
            {item.is_actioned && (
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Check className="h-3 w-3" />
                Actioned
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
