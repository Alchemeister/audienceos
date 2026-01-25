import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, formatDistanceToNow } from "date-fns"
import type { Sentiment, Urgency, Platform } from "./types"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), "MMM d, yyyy")
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), "MMM d, yyyy 'at' h:mm a")
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}

export function formatPercentage(num: number, decimals: number = 1): string {
  return `${(num * 100).toFixed(decimals)}%`
}

export function getSentimentColor(sentiment: Sentiment | string): string {
  switch (sentiment) {
    case "positive":
      return "text-green-600 bg-green-50 border-green-200"
    case "negative":
      return "text-red-600 bg-red-50 border-red-200"
    case "neutral":
      return "text-gray-600 bg-gray-50 border-gray-200"
    case "mixed":
      return "text-yellow-600 bg-yellow-50 border-yellow-200"
    default:
      return "text-gray-600 bg-gray-50 border-gray-200"
  }
}

export function getSentimentBadgeVariant(sentiment: Sentiment | string): "default" | "secondary" | "destructive" | "outline" {
  switch (sentiment) {
    case "positive":
      return "default"
    case "negative":
      return "destructive"
    case "neutral":
      return "secondary"
    case "mixed":
      return "outline"
    default:
      return "secondary"
  }
}

export function getUrgencyColor(urgency: Urgency | string): string {
  switch (urgency) {
    case "critical":
      return "text-red-700 bg-red-100 border-red-300"
    case "high":
      return "text-orange-700 bg-orange-100 border-orange-300"
    case "medium":
      return "text-yellow-700 bg-yellow-100 border-yellow-300"
    case "low":
      return "text-blue-700 bg-blue-100 border-blue-300"
    default:
      return "text-gray-600 bg-gray-100 border-gray-300"
  }
}

export function getPlatformIcon(platform: Platform | string): string {
  switch (platform) {
    case "reddit":
      return "MessageSquare"
    case "twitter":
      return "X"
    case "hackernews":
      return "Newspaper"
    case "github":
      return "Github"
    case "email":
      return "Mail"
    case "widget":
      return "MessageCircle"
    case "manual":
      return "Pencil"
    default:
      return "Globe"
  }
}

export function getPlatformLabel(platform: Platform | string): string {
  switch (platform) {
    case "reddit":
      return "Reddit"
    case "twitter":
      return "X"
    case "hackernews":
      return "Hacker News"
    case "github":
      return "GitHub"
    case "email":
      return "Email"
    case "widget":
      return "Widget"
    case "manual":
      return "Manual"
    default:
      return platform
  }
}

export function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    bug: "Bug Report",
    feature_request: "Feature Request",
    praise: "Praise",
    complaint: "Complaint",
    question: "Question",
    churn_risk: "Churn Risk",
    competitor_mention: "Competitor Mention",
  }
  return labels[category] || category
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + "..."
}
