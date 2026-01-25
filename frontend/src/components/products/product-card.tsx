"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { MoreHorizontal, ExternalLink, MessageSquare, TrendingUp } from "lucide-react"

import type { Product } from "@/lib/types"
import { formatDate } from "@/lib/utils"
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
import { Badge } from "@/components/ui/badge"

interface ProductCardProps {
  product: Product
  onEdit?: (product: Product) => void
  onDelete?: (product: Product) => void
}

export function ProductCard({ product, onEdit, onDelete }: ProductCardProps) {
  const router = useRouter()

  const handleCardClick = (e: React.MouseEvent) => {
    // Don't navigate if clicking on interactive elements
    const target = e.target as HTMLElement
    if (target.closest('button') || target.closest('a') || target.closest('[role="menuitem"]')) {
      return
    }
    router.push(`/products/${product.id}`)
  }

  return (
    <Card
      className="hover:border-primary/50 transition-colors cursor-pointer"
      onClick={handleCardClick}
    >
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div className="space-y-1">
          <CardTitle className="hover:text-primary transition-colors">
            {product.name}
          </CardTitle>
          <CardDescription className="line-clamp-2">
            {product.description}
          </CardDescription>
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
              <Link href={`/products/${product.id}`}>View Dashboard</Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link href={`/products/${product.id}/feedback`}>View Feedback</Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {onEdit && (
              <DropdownMenuItem onClick={() => onEdit(product)}>
                Edit Product
              </DropdownMenuItem>
            )}
            {onDelete && (
              <DropdownMenuItem
                onClick={() => onDelete(product)}
                className="text-destructive focus:text-destructive"
              >
                Delete Product
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* URL */}
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ExternalLink className="h-3 w-3" />
              {new URL(product.url).hostname}
            </a>
          )}

          {/* Keywords */}
          {product.keywords.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {product.keywords.slice(0, 5).map((keyword) => (
                <Badge key={keyword} variant="secondary" className="text-xs">
                  {keyword}
                </Badge>
              ))}
              {product.keywords.length > 5 && (
                <Badge variant="outline" className="text-xs">
                  +{product.keywords.length - 5} more
                </Badge>
              )}
            </div>
          )}

          {/* Stats placeholder */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground pt-2 border-t">
            <div className="flex items-center gap-1">
              <MessageSquare className="h-4 w-4" />
              <span>--</span>
            </div>
            <div className="flex items-center gap-1">
              <TrendingUp className="h-4 w-4" />
              <span>--</span>
            </div>
            <div className="ml-auto text-xs">
              Created {formatDate(product.created_at)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
