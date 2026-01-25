"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface CategoryChartProps {
  data?: Array<{
    category: string
    count: number
  }>
}

// Mock data for demonstration
const mockData = [
  { category: "Feature Request", count: 34 },
  { category: "Bug Report", count: 18 },
  { category: "Praise", count: 45 },
  { category: "Question", count: 22 },
  { category: "Complaint", count: 12 },
  { category: "Suggestion", count: 28 },
]

export function CategoryChart({ data = mockData }: CategoryChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Feedback Categories</CardTitle>
        <CardDescription>What people are talking about</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[250px] sm:h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 10, left: 60, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" horizontal={true} vertical={false} />
              <XAxis
                type="number"
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                type="category"
                dataKey="category"
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                width={75}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--background))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px'
                }}
                formatter={(value: number) => [`${value} mentions`, 'Count']}
              />
              <Bar
                dataKey="count"
                fill="hsl(var(--primary))"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
