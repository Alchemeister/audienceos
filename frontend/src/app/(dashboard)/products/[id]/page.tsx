"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import Link from "next/link"
import {
  MessageSquare,
  Users,
  Megaphone,
  Lightbulb,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  ExternalLink,
  Code,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Plus,
  X,
} from "lucide-react"

import { api } from "@/lib/api"
import { formatNumber, formatPercentage } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { SentimentTrendChart } from "@/components/charts/sentiment-trend-chart"
import { FeedbackSourcesChart } from "@/components/charts/feedback-sources-chart"
import { CategoryChart } from "@/components/charts/category-chart"
import { AIInsightsCard } from "@/components/charts/ai-insights-card"

export default function ProductPage() {
  const params = useParams()
  const id = params.id as string
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data: product, isLoading: productLoading } = useQuery({
    queryKey: ["product", id],
    queryFn: async () => {
      const token = await getToken()
      return api.products.get(token, id)
    },
  })

  const { data: feedbackStats, isLoading: statsLoading } = useQuery({
    queryKey: ["feedback-stats", id],
    queryFn: async () => {
      const token = await getToken()
      return api.feedback.getStats(token, id, 30)
    },
  })

  const updateProductMutation = useMutation({
    mutationFn: async (data: { keywords?: string[]; competitors?: string[] }) => {
      const token = await getToken()
      return api.products.update(token, id, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["product", id] })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update. Please try again.",
        variant: "destructive",
      })
    },
  })

  if (productLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh]">
        <p className="text-muted-foreground">Product not found</p>
        <Link href="/products">
          <Button variant="link">Back to Products</Button>
        </Link>
      </div>
    )
  }

  const sentimentScore = feedbackStats
    ? (feedbackStats.sentiment_counts.positive || 0) / Math.max(feedbackStats.total_count, 1)
    : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{product.name}</h1>
          <p className="text-muted-foreground mt-1">{product.description}</p>
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-2"
            >
              <ExternalLink className="h-3 w-3" />
              {product.url}
            </a>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                formatNumber(feedbackStats?.total_count || 0)
              )}
            </div>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sentiment Score</CardTitle>
            {sentimentScore >= 0.5 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                formatPercentage(sentimentScore)
              )}
            </div>
            <p className="text-xs text-muted-foreground">Positive mentions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Churn Risk</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                feedbackStats?.high_churn_count || 0
              )}
            </div>
            <p className="text-xs text-muted-foreground">High-risk mentions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Actioned</CardTitle>
            <Lightbulb className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                formatPercentage(feedbackStats?.actioned_rate || 0)
              )}
            </div>
            <p className="text-xs text-muted-foreground">Feedback addressed</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <SentimentTrendChart />
        <FeedbackSourcesChart />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <CategoryChart />
        <AIInsightsCard />
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Feedback
            </CardTitle>
            <CardDescription>
              View and manage all feedback for this product
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={`/products/${id}/feedback`}>
              <Button variant="outline" className="w-full">
                View Feedback
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Users className="h-5 w-5" />
              Audiences
            </CardTitle>
            <CardDescription>
              Discover where your target audience hangs out
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={`/products/${id}/audiences`}>
              <Button variant="outline" className="w-full">
                Research Audiences
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Megaphone className="h-5 w-5" />
              Campaigns
            </CardTitle>
            <CardDescription>
              Create and manage marketing campaigns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={`/products/${id}/campaigns`}>
              <Button variant="outline" className="w-full">
                View Campaigns
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Keywords and Competitors */}
      <div className="grid gap-4 md:grid-cols-2">
        <EditableTagCard
          title="Tracked Keywords"
          description="Keywords being monitored for mentions"
          items={product.keywords}
          emptyMessage="No keywords configured"
          variant="secondary"
          onAdd={(keyword) => {
            const newKeywords = [...product.keywords, keyword]
            updateProductMutation.mutate({ keywords: newKeywords })
          }}
          onRemove={(keyword) => {
            const newKeywords = product.keywords.filter((k) => k !== keyword)
            updateProductMutation.mutate({ keywords: newKeywords })
          }}
        />

        <EditableTagCard
          title="Competitors"
          description="Competitors being tracked for mentions"
          items={product.competitors}
          emptyMessage="No competitors configured"
          variant="outline"
          onAdd={(competitor) => {
            const newCompetitors = [...product.competitors, competitor]
            updateProductMutation.mutate({ competitors: newCompetitors })
          }}
          onRemove={(competitor) => {
            const newCompetitors = product.competitors.filter((c) => c !== competitor)
            updateProductMutation.mutate({ competitors: newCompetitors })
          }}
        />
      </div>

      {/* API Integration */}
      <ApiIntegrationCard productId={id} />
    </div>
  )
}

function EditableTagCard({
  title,
  description,
  items,
  emptyMessage,
  variant,
  onAdd,
  onRemove,
}: {
  title: string
  description: string
  items: string[]
  emptyMessage: string
  variant: "secondary" | "outline"
  onAdd: (item: string) => void
  onRemove: (item: string) => void
}) {
  const [isAdding, setIsAdding] = useState(false)
  const [inputValue, setInputValue] = useState("")

  const handleAdd = () => {
    if (inputValue.trim() && !items.includes(inputValue.trim())) {
      onAdd(inputValue.trim())
      setInputValue("")
      setIsAdding(false)
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle className="text-lg">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={() => setIsAdding(!isAdding)}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        {isAdding && (
          <div className="flex gap-2 mb-3">
            <Input
              placeholder={`Add ${title.toLowerCase().slice(0, -1)}...`}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  handleAdd()
                }
                if (e.key === "Escape") {
                  setIsAdding(false)
                  setInputValue("")
                }
              }}
              autoFocus
              className="h-8"
            />
            <Button size="sm" onClick={handleAdd} className="h-8">
              Add
            </Button>
          </div>
        )}
        {items.length === 0 && !isAdding ? (
          <p className="text-sm text-muted-foreground">{emptyMessage}</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {items.map((item) => (
              <Badge key={item} variant={variant} className="gap-1 pr-1">
                {item}
                <button
                  onClick={() => onRemove(item)}
                  className="ml-1 hover:text-destructive rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ApiIntegrationCard({ productId }: { productId: string }) {
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)

  const apiEndpoint = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/feedback/webhook`

  const samplePayload = JSON.stringify({
    product_id: productId,
    text: "Your feedback text here",
    source: "widget",
    source_url: "https://yoursite.com/page",
    author: "User Name (optional)",
    metadata: { page: "/pricing" }
  }, null, 2)

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  return (
    <Card>
      <CardHeader
        className="cursor-pointer select-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Code className="h-5 w-5" />
            API Integration
          </CardTitle>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
        <CardDescription>
          Collect feedback from your website using the webhook API
        </CardDescription>
      </CardHeader>
      {isExpanded && (
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Product ID</label>
            <div className="flex items-center gap-2 mt-1">
              <code className="flex-1 bg-muted px-3 py-2 rounded text-sm font-mono overflow-x-auto">
                {productId}
              </code>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(productId, 'productId')}
              >
                {copiedField === 'productId' ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">Webhook Endpoint</label>
            <div className="flex items-center gap-2 mt-1">
              <code className="flex-1 bg-muted px-3 py-2 rounded text-sm font-mono overflow-x-auto">
                POST {apiEndpoint}
              </code>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(apiEndpoint, 'endpoint')}
              >
                {copiedField === 'endpoint' ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">Sample JSON Payload</label>
            <div className="relative mt-1">
              <pre className="bg-muted px-3 py-2 rounded text-sm font-mono overflow-x-auto whitespace-pre-wrap">
                {samplePayload}
              </pre>
              <Button
                variant="outline"
                size="sm"
                className="absolute top-2 right-2"
                onClick={() => copyToClipboard(samplePayload, 'payload')}
              >
                {copiedField === 'payload' ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            Send a POST request with Content-Type: application/json. The product_id is already set for this product.
          </p>
        </CardContent>
      )}
    </Card>
  )
}
