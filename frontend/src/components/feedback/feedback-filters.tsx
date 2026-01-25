"use client"

import { Search, X } from "lucide-react"

import type { Platform, Sentiment, FeedbackCategory, Urgency } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export interface FeedbackFilters {
  source?: Platform
  sentiment?: Sentiment
  category?: FeedbackCategory
  urgency?: Urgency
  is_actioned?: boolean
  search?: string
}

interface FeedbackFiltersProps {
  filters: FeedbackFilters
  onFiltersChange: (filters: FeedbackFilters) => void
}

const platforms: { value: Platform; label: string }[] = [
  { value: "reddit", label: "Reddit" },
  { value: "twitter", label: "X" },
  { value: "hackernews", label: "Hacker News" },
  { value: "github", label: "GitHub" },
  { value: "email", label: "Email" },
  { value: "widget", label: "Widget" },
  { value: "manual", label: "Manual" },
]

const sentiments: { value: Sentiment; label: string }[] = [
  { value: "positive", label: "Positive" },
  { value: "negative", label: "Negative" },
  { value: "neutral", label: "Neutral" },
  { value: "mixed", label: "Mixed" },
]

const categories: { value: FeedbackCategory; label: string }[] = [
  { value: "bug", label: "Bug Report" },
  { value: "feature_request", label: "Feature Request" },
  { value: "praise", label: "Praise" },
  { value: "complaint", label: "Complaint" },
  { value: "question", label: "Question" },
  { value: "churn_risk", label: "Churn Risk" },
  { value: "competitor_mention", label: "Competitor Mention" },
]

const urgencies: { value: Urgency; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
]

export function FeedbackFilters({
  filters,
  onFiltersChange,
}: FeedbackFiltersProps) {
  const hasFilters = Object.values(filters).some(
    (v) => v !== undefined && v !== ""
  )

  const clearFilters = () => {
    onFiltersChange({})
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search feedback..."
          value={filters.search || ""}
          onChange={(e) =>
            onFiltersChange({ ...filters, search: e.target.value || undefined })
          }
          className="pl-9"
        />
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap gap-2">
        <Select
          value={filters.source || ""}
          onValueChange={(value) =>
            onFiltersChange({
              ...filters,
              source: value ? (value as Platform) : undefined,
            })
          }
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Source" />
          </SelectTrigger>
          <SelectContent>
            {platforms.map((platform) => (
              <SelectItem key={platform.value} value={platform.value}>
                {platform.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.sentiment || ""}
          onValueChange={(value) =>
            onFiltersChange({
              ...filters,
              sentiment: value ? (value as Sentiment) : undefined,
            })
          }
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Sentiment" />
          </SelectTrigger>
          <SelectContent>
            {sentiments.map((sentiment) => (
              <SelectItem key={sentiment.value} value={sentiment.value}>
                {sentiment.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.category || ""}
          onValueChange={(value) =>
            onFiltersChange({
              ...filters,
              category: value ? (value as FeedbackCategory) : undefined,
            })
          }
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map((category) => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.urgency || ""}
          onValueChange={(value) =>
            onFiltersChange({
              ...filters,
              urgency: value ? (value as Urgency) : undefined,
            })
          }
        >
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Urgency" />
          </SelectTrigger>
          <SelectContent>
            {urgencies.map((urgency) => (
              <SelectItem key={urgency.value} value={urgency.value}>
                {urgency.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={
            filters.is_actioned === undefined
              ? ""
              : filters.is_actioned
                ? "true"
                : "false"
          }
          onValueChange={(value) =>
            onFiltersChange({
              ...filters,
              is_actioned:
                value === "" ? undefined : value === "true" ? true : false,
            })
          }
        >
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="false">Not actioned</SelectItem>
            <SelectItem value="true">Actioned</SelectItem>
          </SelectContent>
        </Select>

        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="mr-1 h-4 w-4" />
            Clear
          </Button>
        )}
      </div>
    </div>
  )
}
