"use client"

import { useParams } from "next/navigation"
import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Lightbulb,
  FileText,
  Sparkles,
  Lock,
  RefreshCw,
  Calendar,
} from "lucide-react"

import { api } from "@/lib/api"
import { formatDate, formatPercentage } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { InsightCard } from "@/components/insights/insight-card"

export default function InsightsPage() {
  const params = useParams()
  const productId = params.id as string
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch insights
  const { data: insightsData, isLoading: insightsLoading } = useQuery({
    queryKey: ["insights", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.insights.list(token, { product_id: productId, limit: 20 })
    },
  })

  // Fetch weekly reports
  const { data: reportsData, isLoading: reportsLoading } = useQuery({
    queryKey: ["reports", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.insights.listReports(token, productId, { limit: 5 })
    },
  })

  // Fetch themes
  const { data: themesData, isLoading: themesLoading } = useQuery({
    queryKey: ["themes", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.insights.getThemes(token, productId, true)
    },
  })

  // Fetch credits
  const { data: creditsData } = useQuery({
    queryKey: ["credits"],
    queryFn: async () => {
      const token = await getToken()
      return api.insights.getCredits(token)
    },
  })

  // Action insight mutation
  const actionMutation = useMutation({
    mutationFn: async ({ id, action }: { id: string; action: "action" | "dismiss" }) => {
      const token = await getToken()
      return api.insights.update(token, id, {
        is_actioned: action === "action",
        is_dismissed: action === "dismiss",
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["insights", productId] })
      toast({
        title: "Insight updated",
        description: "The insight has been updated.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update insight.",
        variant: "destructive",
      })
    },
  })

  // Trigger clustering mutation
  const clusterMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken()
      return api.insights.triggerClustering(token, productId)
    },
    onSuccess: () => {
      toast({
        title: "Clustering started",
        description: "Theme clustering has been queued. Check back soon.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to start clustering.",
        variant: "destructive",
      })
    },
  })

  const handleAction = (id: string) => {
    actionMutation.mutate({ id, action: "action" })
  }

  const handleDismiss = (id: string) => {
    actionMutation.mutate({ id, action: "dismiss" })
  }

  const insights = insightsData?.insights || []
  const reports = reportsData?.reports || []
  const themes = themesData?.themes || []
  const isIndieOrFree = creditsData?.tier === "indie" || !creditsData

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Insights</h1>
          <p className="text-muted-foreground">
            AI-generated insights and analysis from your feedback.
          </p>
        </div>
      </div>

      {/* Credits display */}
      {creditsData && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Deep Analysis Credits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                {creditsData.is_unlimited ? (
                  <span className="text-2xl font-bold">Unlimited</span>
                ) : (
                  <>
                    <span className="text-2xl font-bold">
                      {creditsData.credits_remaining}
                    </span>
                    <span className="text-muted-foreground">
                      {" "}/ {creditsData.credits_total} remaining
                    </span>
                  </>
                )}
              </div>
              <Badge variant="outline">{creditsData.tier} tier</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="insights">
        <TabsList>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="themes">Themes</TabsTrigger>
          <TabsTrigger value="reports">Weekly Reports</TabsTrigger>
          <TabsTrigger value="deep" className="flex items-center gap-1">
            Deep Analysis
            {isIndieOrFree && <Lock className="h-3 w-3" />}
          </TabsTrigger>
        </TabsList>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-4 mt-4">
          {insightsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-40" />
              ))}
            </div>
          ) : insights.length === 0 ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <Lightbulb className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-2">No insights yet</h3>
              <p className="text-muted-foreground max-w-sm">
                Insights will be generated automatically as feedback is collected
                and analyzed.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {insights.map((insight) => (
                <InsightCard
                  key={insight.id}
                  insight={insight}
                  onAction={handleAction}
                  onDismiss={handleDismiss}
                />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Themes Tab */}
        <TabsContent value="themes" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {themesData?.last_clustered_at
                ? `Last clustered: ${formatDate(themesData.last_clustered_at)}`
                : "No clustering performed yet"}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => clusterMutation.mutate()}
              disabled={clusterMutation.isPending}
            >
              <RefreshCw
                className={`mr-2 h-4 w-4 ${clusterMutation.isPending ? "animate-spin" : ""}`}
              />
              Re-cluster Themes
            </Button>
          </div>

          {themesLoading ? (
            <div className="grid gap-4 md:grid-cols-2">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-40" />
              ))}
            </div>
          ) : themes.length === 0 ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <Sparkles className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-2">No themes discovered</h3>
              <p className="text-muted-foreground mb-4 max-w-sm">
                Themes are discovered by clustering similar feedback. You need at
                least 10 feedback items.
              </p>
              <Button
                onClick={() => clusterMutation.mutate()}
                disabled={clusterMutation.isPending}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Discover Themes
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {themes.map((theme) => (
                <Card key={theme.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{theme.name}</CardTitle>
                    <CardDescription>{theme.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Feedback count</span>
                      <span className="font-medium">{theme.feedback_count}</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {theme.keywords.slice(0, 5).map((keyword) => (
                        <Badge key={keyword} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                    {Object.keys(theme.sentiment_breakdown).length > 0 && (
                      <div className="flex gap-2 text-xs">
                        {Object.entries(theme.sentiment_breakdown).map(
                          ([sentiment, count]) => (
                            <span key={sentiment} className="text-muted-foreground">
                              {sentiment}: {count}
                            </span>
                          )
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-4 mt-4">
          {reportsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : reports.length === 0 ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-2">No reports yet</h3>
              <p className="text-muted-foreground max-w-sm">
                Weekly reports are generated automatically every Monday with a
                summary of your feedback and campaigns.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {reports.map((report) => (
                <Card key={report.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <CardTitle className="text-base">
                          Week of {formatDate(report.week_start)}
                        </CardTitle>
                      </div>
                      {report.email_sent && (
                        <Badge variant="outline">Email sent</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">New mentions</span>
                        <p className="font-medium">{report.new_mentions}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Sentiment</span>
                        <p className="font-medium">
                          {formatPercentage(report.sentiment_score / 2 + 0.5)}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Change</span>
                        <p
                          className={`font-medium ${
                            report.sentiment_change > 0
                              ? "text-green-600"
                              : report.sentiment_change < 0
                                ? "text-red-600"
                                : ""
                          }`}
                        >
                          {report.sentiment_change > 0 ? "+" : ""}
                          {formatPercentage(report.sentiment_change)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Deep Analysis Tab */}
        <TabsContent value="deep" className="space-y-4 mt-4">
          {isIndieOrFree ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <Lock className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-2">Upgrade to Pro</h3>
              <p className="text-muted-foreground mb-4 max-w-sm">
                Deep analysis features like churn analysis, competitor intelligence,
                and content strategy are available on Pro and Agency plans.
              </p>
              <Button>Upgrade to Pro</Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              <Card className="cursor-pointer hover:border-primary/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-lg">Churn Analysis</CardTitle>
                  <CardDescription>
                    Identify at-risk customers and understand why they might leave.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">
                    Run Analysis
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:border-primary/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-lg">Competitor Intelligence</CardTitle>
                  <CardDescription>
                    Analyze how competitors are perceived and find opportunities.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">
                    Run Analysis
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:border-primary/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-lg">Content Strategy</CardTitle>
                  <CardDescription>
                    Get AI recommendations for content that resonates with your audience.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">
                    Run Analysis
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
