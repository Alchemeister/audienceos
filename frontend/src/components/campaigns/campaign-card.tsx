"use client"

import Link from "next/link"
import { MoreHorizontal, MousePointer, Target, TrendingUp } from "lucide-react"

import type { Campaign } from "@/lib/types"
import { formatNumber, formatPercentage, formatRelativeTime } from "@/lib/utils"
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface CampaignCardProps {
  campaign: Campaign
  productId: string
  onEdit?: (campaign: Campaign) => void
  onDelete?: (campaign: Campaign) => void
}

const statusVariants: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "outline",
  active: "default",
  completed: "secondary",
  archived: "destructive",
}

export function CampaignCard({
  campaign,
  productId,
  onEdit,
  onDelete,
}: CampaignCardProps) {
  return (
    <Card className="hover:border-primary/50 transition-colors">
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Link href={`/products/${productId}/campaigns/${campaign.id}`}>
              <CardTitle className="hover:text-primary transition-colors cursor-pointer">
                {campaign.name}
              </CardTitle>
            </Link>
            <Badge variant={statusVariants[campaign.status] || "outline"}>
              {campaign.status}
            </Badge>
          </div>
          {campaign.description && (
            <CardDescription className="line-clamp-2">
              {campaign.description}
            </CardDescription>
          )}
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">Open menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/products/${productId}/campaigns/${campaign.id}`}>
                View Details
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {onEdit && (
              <DropdownMenuItem onClick={() => onEdit(campaign)}>
                Edit Campaign
              </DropdownMenuItem>
            )}
            {onDelete && (
              <DropdownMenuItem
                onClick={() => onDelete(campaign)}
                className="text-destructive focus:text-destructive"
              >
                Delete Campaign
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Target subreddits */}
          {campaign.target_subreddits.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {campaign.target_subreddits.slice(0, 3).map((subreddit) => (
                <Badge key={subreddit} variant="secondary" className="text-xs">
                  r/{subreddit}
                </Badge>
              ))}
              {campaign.target_subreddits.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{campaign.target_subreddits.length - 3} more
                </Badge>
              )}
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 pt-2 border-t">
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <MousePointer className="h-3 w-3" />
                Clicks
              </span>
              <span className="text-lg font-semibold">
                {formatNumber(campaign.total_clicks)}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Target className="h-3 w-3" />
                Conversions
              </span>
              <span className="text-lg font-semibold">
                {formatNumber(campaign.total_conversions)}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                Rate
              </span>
              <span className="text-lg font-semibold">
                {formatPercentage(campaign.conversion_rate)}
              </span>
            </div>
          </div>

          {/* Footer */}
          <div className="text-xs text-muted-foreground">
            Created {formatRelativeTime(campaign.created_at)}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
