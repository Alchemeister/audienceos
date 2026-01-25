"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useEffect } from "react"
import {
  LayoutDashboard,
  MessageSquare,
  Users,
  Megaphone,
  Lightbulb,
  Settings,
  Package,
  ChevronLeft,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  // Extract productId from URL if on a product page
  const productMatch = pathname.match(/^\/products\/([^/]+)/)
  const productId = productMatch ? productMatch[1] : null

  // Load collapsed state from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-collapsed")
    if (stored !== null) {
      setCollapsed(stored === "true")
    }
  }, [])

  // Save collapsed state to localStorage
  const toggleCollapsed = () => {
    const newState = !collapsed
    setCollapsed(newState)
    localStorage.setItem("sidebar-collapsed", String(newState))
  }

  const productNavItems = productId
    ? [
        {
          title: "Overview",
          href: `/products/${productId}`,
          icon: LayoutDashboard,
        },
        {
          title: "Feedback",
          href: `/products/${productId}/feedback`,
          icon: MessageSquare,
        },
        {
          title: "Audiences",
          href: `/products/${productId}/audiences`,
          icon: Users,
        },
        {
          title: "Campaigns",
          href: `/products/${productId}/campaigns`,
          icon: Megaphone,
        },
        {
          title: "Insights",
          href: `/products/${productId}/insights`,
          icon: Lightbulb,
        },
      ]
    : []

  const mainNavItems = [
    {
      title: "Products",
      href: "/products",
      icon: Package,
    },
    {
      title: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ]

  const NavItem = ({ item, isActive }: { item: typeof mainNavItems[0], isActive: boolean }) => {
    const content = (
      <Button
        variant={isActive ? "secondary" : "ghost"}
        size="sm"
        className={cn(
          "w-full",
          collapsed ? "justify-center px-2" : "justify-start",
          isActive && "bg-secondary"
        )}
      >
        <item.icon className={cn("h-4 w-4", !collapsed && "mr-2")} />
        {!collapsed && item.title}
      </Button>
    )

    if (collapsed) {
      return (
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <Link href={item.href}>{content}</Link>
          </TooltipTrigger>
          <TooltipContent side="right">
            {item.title}
          </TooltipContent>
        </Tooltip>
      )
    }

    return <Link href={item.href}>{content}</Link>
  }

  return (
    <TooltipProvider>
      <div className={cn(
        "flex h-full flex-col bg-background transition-all duration-200",
        collapsed ? "w-14" : "w-64"
      )}>
        {/* Collapse toggle at top */}
        <div className={cn(
          "flex items-center h-10 border-b",
          collapsed ? "justify-center px-2" : "justify-end px-3"
        )}>
          <Tooltip delayDuration={0}>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleCollapsed}
                className="h-7 w-7"
              >
                {collapsed ? (
                  <PanelLeft className="h-4 w-4" />
                ) : (
                  <PanelLeftClose className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              {collapsed ? "Expand sidebar" : "Collapse sidebar"}
            </TooltipContent>
          </Tooltip>
        </div>

        <ScrollArea className="flex-1 px-2 py-4">
          {/* Back to products when viewing a product */}
          {productId && (
            <>
              {collapsed ? (
                <Tooltip delayDuration={0}>
                  <TooltipTrigger asChild>
                    <Link href="/products">
                      <Button variant="ghost" size="sm" className="w-full justify-center mb-2 px-2">
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">All Products</TooltipContent>
                </Tooltip>
              ) : (
                <Link href="/products">
                  <Button variant="ghost" size="sm" className="w-full justify-start mb-2">
                    <ChevronLeft className="mr-2 h-4 w-4" />
                    All Products
                  </Button>
                </Link>
              )}
              <Separator className="mb-4" />
            </>
          )}

          {/* Product navigation */}
          {productNavItems.length > 0 && (
            <div className="space-y-1">
              {!collapsed && (
                <h4 className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Product
                </h4>
              )}
              {productNavItems.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== `/products/${productId}` &&
                    pathname.startsWith(item.href))

                return <NavItem key={item.href} item={item} isActive={isActive} />
              })}
              <Separator className="my-4" />
            </div>
          )}

          {/* Main navigation */}
          <div className="space-y-1">
            {!collapsed && (
              <h4 className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                Account
              </h4>
            )}
            {mainNavItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
              return <NavItem key={item.href} item={item} isActive={isActive} />
            })}
          </div>
        </ScrollArea>
      </div>
    </TooltipProvider>
  )
}
