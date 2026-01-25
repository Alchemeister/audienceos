"use client"

import {
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  CheckCircle,
  AlertTriangle,
} from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

import type { FeedbackStats as FeedbackStatsType } from "@/lib/types"
import { formatNumber, formatPercentage } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface FeedbackStatsProps {
  stats: FeedbackStatsType | undefined
  isLoading: boolean
}

export function FeedbackStats({ stats, isLoading }: FeedbackStatsProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
    )
  }

  if (!stats) {
    return null
  }

  const positiveRate = stats.total_count > 0
    ? (stats.sentiment_counts.positive || 0) / stats.total_count
    : 0
  const negativeRate = stats.total_count > 0
    ? (stats.sentiment_counts.negative || 0) / stats.total_count
    : 0

  return (
    <div className="space-y-6">
      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(stats.total_count)}
            </div>
            <p className="text-xs text-muted-foreground">
              Last {stats.period_days} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Positive</CardTitle>
            <ThumbsUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatPercentage(positiveRate)}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatNumber(stats.sentiment_counts.positive || 0)} mentions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Negative</CardTitle>
            <ThumbsDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatPercentage(negativeRate)}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatNumber(stats.sentiment_counts.negative || 0)} mentions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Churn Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {stats.high_churn_count}
            </div>
            <p className="text-xs text-muted-foreground">
              High-risk mentions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Actioned</CardTitle>
            <CheckCircle className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatPercentage(stats.actioned_rate)}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatNumber(stats.actioned_count)} addressed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Sentiment trend chart */}
      {stats.sentiment_trend.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Sentiment Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats.sentiment_trend}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    domain={[-1, 1]}
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="rounded-lg border bg-background p-2 shadow-sm">
                            <p className="text-sm font-medium">{label}</p>
                            <p className="text-sm text-muted-foreground">
                              Score: {((payload[0].value as number) * 100).toFixed(1)}%
                            </p>
                            <p className="text-sm text-muted-foreground">
                              Count: {payload[0].payload.count}
                            </p>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top phrases */}
      {stats.top_phrases.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Phrases</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {stats.top_phrases.slice(0, 15).map((item, index) => (
                <div
                  key={index}
                  className="inline-flex items-center gap-1 rounded-full bg-muted px-3 py-1 text-sm"
                >
                  <span>{item.phrase}</span>
                  <span className="text-xs text-muted-foreground">
                    ({item.count})
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
