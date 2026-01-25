"use client"

import { useParams } from "next/navigation"
import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Megaphone, Plus } from "lucide-react"

import { api } from "@/lib/api"
import type { Campaign, CampaignCreate } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { CampaignCard } from "@/components/campaigns/campaign-card"
import { CreateCampaignDialog } from "@/components/campaigns/create-campaign-dialog"

export default function CampaignsPage() {
  const params = useParams()
  const productId = params.id as string
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch campaigns
  const { data: campaignsData, isLoading } = useQuery({
    queryKey: ["campaigns", productId],
    queryFn: async () => {
      const token = await getToken()
      return api.campaigns.list(token, { product_id: productId })
    },
  })

  // Create campaign mutation
  const createMutation = useMutation({
    mutationFn: async (data: CampaignCreate) => {
      const token = await getToken()
      return api.campaigns.create(token, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", productId] })
      toast({
        title: "Campaign created",
        description: "Your campaign has been created successfully.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create campaign. Please try again.",
        variant: "destructive",
      })
    },
  })

  // Delete campaign mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken()
      return api.campaigns.delete(token, id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", productId] })
      toast({
        title: "Campaign deleted",
        description: "Your campaign has been deleted successfully.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to delete campaign. Please try again.",
        variant: "destructive",
      })
    },
  })

  const handleCreate = async (data: CampaignCreate) => {
    await createMutation.mutateAsync(data)
  }

  const handleDelete = (campaign: Campaign) => {
    if (
      confirm(
        `Are you sure you want to delete "${campaign.name}"? This will also delete all generated posts and tracking links.`
      )
    ) {
      deleteMutation.mutate(campaign.id)
    }
  }

  const campaigns = campaignsData?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Campaigns</h1>
          <p className="text-muted-foreground">
            Create and manage marketing campaigns with AI-generated content.
          </p>
        </div>
        <CreateCampaignDialog productId={productId} onSubmit={handleCreate} />
      </div>

      {/* Campaigns list */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : campaigns.length === 0 ? (
        <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
          <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
            <Megaphone className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold mb-2">No campaigns yet</h3>
          <p className="text-muted-foreground mb-4 max-w-sm">
            Create your first campaign to start generating content and tracking
            conversions.
          </p>
          <CreateCampaignDialog
            productId={productId}
            onSubmit={handleCreate}
            trigger={
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Campaign
              </Button>
            }
          />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((campaign) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              productId={productId}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
