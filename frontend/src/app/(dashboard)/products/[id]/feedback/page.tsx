"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { RefreshCw, MessageSquare, Loader2 } from "lucide-react"

import { api } from "@/lib/api"
import type { FeedbackFilterParams, FeedbackItem as FeedbackItemType } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { FeedbackItem } from "@/components/feedback/feedback-item"
import { FeedbackFilters, type FeedbackFilters as FiltersType } from "@/components/feedback/feedback-filters"
import { FeedbackStats } from "@/components/feedback/feedback-stats"

const PAGE_SIZE = 50

export default function FeedbackPage() {
  const params = useParams()
  const productId = params.id as string
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [filters, setFilters] = useState<FiltersType>({})

  // Reset pagination when filters change
  const handleFiltersChange = (newFilters: FiltersType) => {
    setFilters(newFilters)
    setAllFeedback([])
    setCurrentOffset(0)
  }
  const [activeTab, setActiveTab] = useState<"feed" | "stats">("feed")
  const [allFeedback, setAllFeedback] = useState<FeedbackItemType[]>([])
  const [currentOffset, setCurrentOffset] = useState(0)
  const [isLoadingMore, setIsLoadingMore] = useState(false)

  // Build query params
  const queryParams: FeedbackFilterParams = {
    product_id: productId,
    ...filters,
    limit: PAGE_SIZE,
    offset: 0,
  }

  // Fetch feedback (initial load)
  const {
    data: feedbackData,
    isLoading: feedbackLoading,
    refetch: refetchFeedback,
    isFetching: feedbackFetching,
  } = useQuery({
    queryKey: ["feedback", productId, filters],
    queryFn: async () => {
      const token = await getToken()
      const result = await api.feedback.list(token, queryParams)
      setAllFeedback(result.items)
      setCurrentOffset(PAGE_SIZE)
      return result
    },
    refetchInterval: 30000, // Poll every 30 seconds
  })

  // Load more function
  const handleLoadMore = async () => {
    setIsLoadingMore(true)
    try {
      const token = await getToken()
      const result = await api.feedback.list(token, {
        ...queryParams,
        offset: currentOffset,
      })
      setAllFeedback((prev) => [...prev, ...result.items])
      setCurrentOffset((prev) => prev + PAGE_SIZE)
    } catch {
      toast({
        title: "Error",
        description: "Failed to load more feedback.",
        variant: "destructive",
      })
    } finally {
      setIsLoadingMore(false)
    }
  }

  // Fetch stats
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ["feedback-stats", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.feedback.getStats(token, productId, 30)
    },
  })

  // Mark as actioned mutation
  const actionMutation = useMutation({
    mutationFn: async (feedbackId: string) => {
      const token = await getToken()
      return api.feedback.markActioned(token, feedbackId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["feedback", productId] })
      queryClient.invalidateQueries({ queryKey: ["feedback-stats", productId] })
      toast({
        title: "Feedback actioned",
        description: "The feedback has been marked as actioned.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to mark feedback as actioned.",
        variant: "destructive",
      })
    },
  })

  const handleMarkActioned = (id: string) => {
    actionMutation.mutate(id)
  }

  const feedback = allFeedback.length > 0 ? allFeedback : feedbackData?.items || []
  const totalFeedback = feedbackData?.total || 0
  const hasMore = feedback.length < totalFeedback

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Feedback</h1>
          <p className="text-muted-foreground">
            {totalFeedback} total mentions collected
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetchFeedback()}
          disabled={feedbackFetching}
        >
          <RefreshCw
            className={`mr-2 h-4 w-4 ${feedbackFetching ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "feed" | "stats")}>
        <TabsList>
          <TabsTrigger value="feed">Feed</TabsTrigger>
          <TabsTrigger value="stats">Statistics</TabsTrigger>
        </TabsList>

        <TabsContent value="feed" className="space-y-4 mt-4">
          {/* Filters */}
          <FeedbackFilters filters={filters} onFiltersChange={handleFiltersChange} />

          {/* Feedback list */}
          {feedbackLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          ) : feedback.length === 0 ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <MessageSquare className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-2">No feedback found</h3>
              <p className="text-muted-foreground max-w-sm">
                {Object.keys(filters).length > 0
                  ? "Try adjusting your filters to see more results."
                  : "Feedback will appear here as it's collected from various sources."}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {feedback.map((item) => (
                <FeedbackItem
                  key={item.id}
                  item={item}
                  onMarkActioned={handleMarkActioned}
                />
              ))}
            </div>
          )}

          {/* Load more */}
          {feedback.length > 0 && hasMore && (
            <div className="text-center space-y-2">
              <p className="text-sm text-muted-foreground">
                Showing {feedback.length} of {totalFeedback} items
              </p>
              <Button
                variant="outline"
                onClick={handleLoadMore}
                disabled={isLoadingMore}
              >
                {isLoadingMore ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  `Load More (${totalFeedback - feedback.length} remaining)`
                )}
              </Button>
            </div>
          )}
        </TabsContent>

        <TabsContent value="stats" className="mt-4">
          <FeedbackStats stats={statsData} isLoading={statsLoading} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
