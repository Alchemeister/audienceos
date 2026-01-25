"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Search, Users, Loader2, Sparkles } from "lucide-react"

import { api } from "@/lib/api"
import { formatRelativeTime } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { AudienceSourceCard } from "@/components/audiences/audience-source-card"

export default function AudiencesPage() {
  const params = useParams()
  const productId = params.id as string
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [researchOpen, setResearchOpen] = useState(false)
  const [productDescription, setProductDescription] = useState("")

  // Fetch product
  const { data: product } = useQuery({
    queryKey: ["product", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.products.get(token, productId)
    },
  })

  // Fetch audience research history
  const { data: researchData, isLoading: researchLoading } = useQuery({
    queryKey: ["audiences", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.audiences.list(token, productId, { limit: 10 })
    },
  })

  // Research mutation
  const researchMutation = useMutation({
    mutationFn: async (description: string) => {
      const token = await getToken()
      return api.audiences.research(token, productId, {
        product_description: description,
      })
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["audiences", productId] })
      setResearchOpen(false)
      setProductDescription("")
      toast({
        title: "Research complete",
        description: `Found ${data.sources.length} relevant audience sources.`,
      })
    },
    onError: () => {
      toast({
        title: "Research failed",
        description: "Failed to complete audience research. Please try again.",
        variant: "destructive",
      })
    },
  })

  const handleResearch = () => {
    if (!productDescription.trim()) {
      toast({
        title: "Description required",
        description: "Please provide a product description for the research.",
        variant: "destructive",
      })
      return
    }
    researchMutation.mutate(productDescription)
  }

  const latestResearch = researchData?.items?.[0]
  const allSources = latestResearch?.sources || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audiences</h1>
          <p className="text-muted-foreground">
            Discover where your target audience hangs out online.
          </p>
        </div>
        <Dialog open={researchOpen} onOpenChange={setResearchOpen}>
          <DialogTrigger asChild>
            <Button>
              <Search className="mr-2 h-4 w-4" />
              Research Audiences
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Research Audiences</DialogTitle>
              <DialogDescription>
                AI will analyze your product and find relevant communities where
                your target audience discusses similar topics.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Product Description</label>
                <Textarea
                  placeholder="Describe your product, target audience, and the problems you solve..."
                  value={productDescription}
                  onChange={(e) => setProductDescription(e.target.value)}
                  rows={5}
                  defaultValue={product?.description}
                />
                <p className="text-xs text-muted-foreground">
                  A detailed description helps AI find more relevant audiences.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setResearchOpen(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleResearch}
                disabled={researchMutation.isPending}
              >
                {researchMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Researching...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Start Research
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Latest research info */}
      {latestResearch && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">Latest Research</CardTitle>
                <CardDescription>
                  Completed {formatRelativeTime(latestResearch.created_at)}
                </CardDescription>
              </div>
              <Badge
                variant={
                  latestResearch.confidence === "high"
                    ? "default"
                    : latestResearch.confidence === "medium"
                      ? "secondary"
                      : "outline"
                }
              >
                {latestResearch.confidence} confidence
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Discovered keywords */}
              {latestResearch.keywords.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2">Discovered Keywords</p>
                  <div className="flex flex-wrap gap-1">
                    {latestResearch.keywords.map((keyword) => (
                      <Badge key={keyword} variant="secondary">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Competitors mentioned */}
              {latestResearch.competitors_mentioned.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2">Competitors Found</p>
                  <div className="flex flex-wrap gap-1">
                    {latestResearch.competitors_mentioned.map((competitor) => (
                      <Badge key={competitor} variant="outline">
                        {competitor}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Audience sources */}
      {researchLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : allSources.length === 0 ? (
        <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
          <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
            <Users className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold mb-2">No audiences discovered yet</h3>
          <p className="text-muted-foreground mb-4 max-w-sm">
            Run audience research to discover communities where your target
            audience discusses relevant topics.
          </p>
          <Button onClick={() => setResearchOpen(true)}>
            <Search className="mr-2 h-4 w-4" />
            Start Research
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">
            Discovered Sources ({allSources.length})
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {allSources.map((source) => (
              <AudienceSourceCard key={source.id} source={source} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
