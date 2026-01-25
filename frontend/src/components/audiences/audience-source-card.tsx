"use client"

import { ExternalLink, Users, MessageSquare } from "lucide-react"

import type { AudienceSource } from "@/lib/types"
import { formatNumber, formatRelativeTime, getPlatformLabel } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface AudienceSourceCardProps {
  source: AudienceSource
}

export function AudienceSourceCard({ source }: AudienceSourceCardProps) {
  const relevancePercent = source.relevance_score * 100

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{source.name}</CardTitle>
            <Badge variant="outline">{getPlatformLabel(source.platform)}</Badge>
          </div>
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Relevance score */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Relevance</span>
            <span className="font-medium">{relevancePercent.toFixed(0)}%</span>
          </div>
          <Progress value={relevancePercent} className="h-2" />
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-sm">
          {source.monthly_active && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Users className="h-4 w-4" />
              <span>{formatNumber(source.monthly_active)} members</span>
            </div>
          )}
          <div className="flex items-center gap-1 text-muted-foreground">
            <MessageSquare className="h-4 w-4" />
            <span>{source.recent_relevant_posts} relevant posts</span>
          </div>
        </div>

        {/* AI reasoning */}
        <div className="bg-muted/50 rounded-md p-3">
          <p className="text-xs text-muted-foreground mb-1">Why this source:</p>
          <p className="text-sm">{source.reasoning}</p>
        </div>

        {/* Last checked */}
        <p className="text-xs text-muted-foreground">
          Last checked {formatRelativeTime(source.last_checked)}
        </p>
      </CardContent>
    </Card>
  )
}
