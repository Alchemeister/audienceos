"use client"

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface FeedbackSourcesChartProps {
  data?: Array<{
    name: string
    value: number
    color: string
  }>
}

// Mock data for demonstration
const mockData = [
  { name: "Reddit", value: 45, color: "hsl(16, 100%, 50%)" },
  { name: "X", value: 28, color: "hsl(203, 89%, 53%)" },
  { name: "Hacker News", value: 15, color: "hsl(25, 95%, 53%)" },
  { name: "Email", value: 8, color: "hsl(262, 83%, 58%)" },
  { name: "Widget", value: 4, color: "hsl(142, 76%, 36%)" },
]

export function FeedbackSourcesChart({ data = mockData }: FeedbackSourcesChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feedback by Source</CardTitle>
        <CardDescription>Where your feedback is coming from</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[280px] sm:h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                paddingAngle={2}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={{ stroke: 'hsl(var(--muted-foreground))', strokeWidth: 1 }}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--background))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px'
                }}
                formatter={(value: number) => [`${value} mentions`, 'Count']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-wrap justify-center gap-4 mt-4">
          {data.map((item) => (
            <div key={item.name} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-muted-foreground">
                {item.name}: {item.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
