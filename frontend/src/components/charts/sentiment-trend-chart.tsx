"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface SentimentTrendChartProps {
  data?: Array<{
    date: string
    positive: number
    neutral: number
    negative: number
  }>
}

// Mock data for demonstration
const mockData = [
  { date: "Jan 1", positive: 12, neutral: 5, negative: 3 },
  { date: "Jan 8", positive: 15, neutral: 8, negative: 2 },
  { date: "Jan 15", positive: 18, neutral: 6, negative: 4 },
  { date: "Jan 22", positive: 14, neutral: 9, negative: 5 },
  { date: "Jan 29", positive: 22, neutral: 7, negative: 3 },
  { date: "Feb 5", positive: 25, neutral: 10, negative: 2 },
  { date: "Feb 12", positive: 28, neutral: 8, negative: 4 },
  { date: "Feb 19", positive: 24, neutral: 12, negative: 3 },
]

export function SentimentTrendChart({ data = mockData }: SentimentTrendChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiment Over Time</CardTitle>
        <CardDescription>Weekly feedback sentiment trends</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[250px] sm:h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--background))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="positive"
                stroke="hsl(142, 76%, 36%)"
                strokeWidth={2}
                dot={{ fill: "hsl(142, 76%, 36%)" }}
                name="Positive"
              />
              <Line
                type="monotone"
                dataKey="neutral"
                stroke="hsl(var(--muted-foreground))"
                strokeWidth={2}
                dot={{ fill: "hsl(var(--muted-foreground))" }}
                name="Neutral"
              />
              <Line
                type="monotone"
                dataKey="negative"
                stroke="hsl(0, 84%, 60%)"
                strokeWidth={2}
                dot={{ fill: "hsl(0, 84%, 60%)" }}
                name="Negative"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
