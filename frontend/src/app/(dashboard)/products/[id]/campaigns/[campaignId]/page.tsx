"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  ArrowLeft,
  Copy,
  Check,
  ExternalLink,
  Link as LinkIcon,
  Loader2,
  MousePointer,
  Plus,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react"

import { api } from "@/lib/api"
import type { TrackedLinkCreate, ContentGenerateRequest } from "@/lib/types"
import { formatNumber, formatPercentage } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"

const statusVariants: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "outline",
  active: "default",
  completed: "secondary",
  archived: "destructive",
}

export default function CampaignDetailPage() {
  const params = useParams()
  const productId = params.id as string
  const campaignId = params.campaignId as string
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch campaign
  const { data: campaign, isLoading } = useQuery({
    queryKey: ["campaign", campaignId],
    queryFn: async () => {
      const token = await getToken()
      return api.campaigns.get(token, campaignId)
    },
  })

  // Fetch tracked links
  const { data: linksData } = useQuery({
    queryKey: ["tracked-links", campaignId],
    queryFn: async () => {
      const token = await getToken()
      return api.tracking.listLinks(token, { campaign_id: campaignId })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    )
  }

  if (!campaign) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh]">
        <p className="text-muted-foreground">Campaign not found</p>
        <Link href={`/products/${productId}/campaigns`}>
          <Button variant="link">Back to Campaigns</Button>
        </Link>
      </div>
    )
  }

  const links = linksData?.items || campaign.links || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            href={`/products/${productId}/campaigns`}
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Campaigns
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{campaign.name}</h1>
            <Badge variant={statusVariants[campaign.status] || "outline"}>
              {campaign.status}
            </Badge>
          </div>
          {campaign.description && (
            <p className="text-muted-foreground mt-1">{campaign.description}</p>
          )}
        </div>
        <GenerateContentDialog
          campaignId={campaignId}
          targetSubreddits={campaign.target_subreddits}
        />
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clicks</CardTitle>
            <MousePointer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(campaign.total_clicks)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversions</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(campaign.total_conversions)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatPercentage(campaign.conversion_rate)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Target Subreddits */}
      {campaign.target_subreddits.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Target Subreddits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {campaign.target_subreddits.map((subreddit) => (
                <Badge key={subreddit} variant="secondary">
                  r/{subreddit}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tracked Links */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <LinkIcon className="h-5 w-5" />
              Tracked Links
            </CardTitle>
            <CardDescription>
              Create tracked links to measure clicks and conversions from your campaigns
            </CardDescription>
          </div>
          <CreateTrackedLinkDialog campaignId={campaignId} productId={productId} />
        </CardHeader>
        <CardContent>
          {links.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <LinkIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No tracked links yet</p>
              <p className="text-sm">Create a tracked link to start measuring your campaign performance</p>
            </div>
          ) : (
            <div className="space-y-4">
              {links.map((link) => (
                <TrackedLinkCard key={link.id} link={link} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Generated Posts */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Generated Posts
            </CardTitle>
            <CardDescription>
              AI-generated content for your target communities
            </CardDescription>
          </div>
          {campaign.posts && campaign.posts.length > 0 && (
            <GenerateContentDialog
              campaignId={campaignId}
              targetSubreddits={campaign.target_subreddits}
            />
          )}
        </CardHeader>
        <CardContent>
          {!campaign.posts || campaign.posts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Sparkles className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No content generated yet</p>
              <p className="text-sm mb-4">Generate AI content for your target subreddits</p>
              <GenerateContentDialog
                campaignId={campaignId}
                targetSubreddits={campaign.target_subreddits}
              />
            </div>
          ) : (
            <div className="space-y-4">
              {campaign.posts.map((post) => (
                <GeneratedPostCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function TrackedLinkCard({ link }: { link: { id: string; short_url: string; destination_url: string; utm_source: string; clicks: number; conversions: number; conversion_rate: number } }) {
  const [copied, setCopied] = useState<string | null>(null)

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopied(field)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <Badge variant="secondary">{link.utm_source}</Badge>
        <div className="flex items-center gap-4 text-sm">
          <span className="flex items-center gap-1">
            <MousePointer className="h-3 w-3" />
            {formatNumber(link.clicks)} clicks
          </span>
          <span className="flex items-center gap-1">
            <Target className="h-3 w-3" />
            {formatNumber(link.conversions)} conversions
          </span>
          <span className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3" />
            {formatPercentage(link.conversion_rate)}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        <div>
          <label className="text-xs text-muted-foreground">Short URL (use this in your ads)</label>
          <div className="flex items-center gap-2 mt-1">
            <code className="flex-1 bg-muted px-3 py-2 rounded text-sm font-mono overflow-x-auto">
              {link.short_url}
            </code>
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(link.short_url, `short-${link.id}`)}
            >
              {copied === `short-${link.id}` ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <div>
          <label className="text-xs text-muted-foreground">Destination</label>
          <p className="text-sm truncate">{link.destination_url}</p>
        </div>
      </div>
    </div>
  )
}

function GeneratedPostCard({ post }: { post: { id: string; target_community: string; style: string; title?: string | null; body: string; is_posted: boolean; post_url?: string | null } }) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    const text = post.title ? `${post.title}\n\n${post.body}` : post.body
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="border rounded-lg p-4 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">r/{post.target_community}</Badge>
          <Badge variant="outline">{post.style}</Badge>
        </div>
        <Button variant="ghost" size="sm" onClick={copyToClipboard}>
          {copied ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </Button>
      </div>
      {post.title && (
        <h4 className="font-semibold">{post.title}</h4>
      )}
      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
        {post.body}
      </p>
      {post.is_posted && post.post_url && (
        <a
          href={post.post_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
        >
          <ExternalLink className="h-3 w-3" />
          View Post
        </a>
      )}
    </div>
  )
}

function GenerateContentDialog({
  campaignId,
  targetSubreddits,
}: {
  campaignId: string
  targetSubreddits: string[]
}) {
  const [open, setOpen] = useState(false)
  const [subreddit, setSubreddit] = useState("")
  const [topicHint, setTopicHint] = useState("")
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const generateMutation = useMutation({
    mutationFn: async (data: ContentGenerateRequest) => {
      const token = await getToken()
      return api.campaigns.generateContent(token, campaignId, data)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] })
      toast({
        title: "Content generated",
        description: `Generated ${data.posts.length} post variations for r/${data.subreddit}.`,
      })
      setOpen(false)
      setSubreddit("")
      setTopicHint("")
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to generate content. Please try again.",
        variant: "destructive",
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!subreddit) return

    generateMutation.mutate({
      subreddit: subreddit.replace(/^r\//, ""), // Strip r/ prefix if present
      topic_hint: topicHint || undefined,
      include_rules: true,
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate Content
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate AI Content</DialogTitle>
          <DialogDescription>
            Generate community-appropriate content for a target subreddit. The AI will create multiple post variations.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="subreddit">Target Subreddit</Label>
            {targetSubreddits.length > 0 ? (
              <Select value={subreddit} onValueChange={setSubreddit}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a subreddit" />
                </SelectTrigger>
                <SelectContent>
                  {targetSubreddits.map((sub) => (
                    <SelectItem key={sub} value={sub}>
                      r/{sub}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                id="subreddit"
                placeholder="e.g., SaaS, startups, webdev"
                value={subreddit}
                onChange={(e) => setSubreddit(e.target.value)}
                required
              />
            )}
            <p className="text-xs text-muted-foreground">
              {targetSubreddits.length > 0
                ? "Select from your campaign's target subreddits"
                : "Enter the subreddit name (without r/)"}
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="topic">Topic Hint (optional)</Label>
            <Input
              id="topic"
              placeholder="e.g., productivity tips, API monitoring"
              value={topicHint}
              onChange={(e) => setTopicHint(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Give the AI a specific angle or topic to focus on
            </p>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={generateMutation.isPending || !subreddit}>
              {generateMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                "Generate"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function CreateTrackedLinkDialog({ campaignId, productId }: { campaignId: string; productId: string }) {
  const [open, setOpen] = useState(false)
  const [destinationUrl, setDestinationUrl] = useState("")
  const [utmSource, setUtmSource] = useState("")
  const { getToken } = useAuthToken()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: async (data: TrackedLinkCreate) => {
      const token = await getToken()
      return api.tracking.createLink(token, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracked-links", campaignId] })
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] })
      toast({
        title: "Link created",
        description: "Your tracked link has been created successfully.",
      })
      setOpen(false)
      setDestinationUrl("")
      setUtmSource("")
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create tracked link. Please try again.",
        variant: "destructive",
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!destinationUrl || !utmSource) return

    createMutation.mutate({
      campaign_id: campaignId,
      destination_url: destinationUrl,
      utm_source: utmSource,
      utm_medium: "organic",
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Link
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Tracked Link</DialogTitle>
          <DialogDescription>
            Create a tracked link for your campaign. Use the generated short URL in your ads.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="destination">Destination URL</Label>
            <Input
              id="destination"
              placeholder="https://yoursite.com"
              value={destinationUrl}
              onChange={(e) => setDestinationUrl(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground">
              Where users will be redirected after clicking
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="source">Source</Label>
            <Input
              id="source"
              placeholder="facebook, reddit, x..."
              value={utmSource}
              onChange={(e) => setUtmSource(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground">
              Where you'll be posting this link (used for UTM tracking)
            </p>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creating..." : "Create Link"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
