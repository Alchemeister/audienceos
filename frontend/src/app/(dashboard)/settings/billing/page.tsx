"use client"

import { useAuthToken } from "@/hooks/use-auth-token"
import { useQuery } from "@tanstack/react-query"
import { CreditCard, Check, Package, Key, Sparkles } from "lucide-react"

import { api } from "@/lib/api"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"

const plans = [
  {
    name: "Indie",
    price: "$39",
    description: "For indie hackers",
    features: ["1 product", "10 keywords", "2-week backfill"],
    current: false,
  },
  {
    name: "Pro",
    price: "$99",
    description: "For growing startups",
    features: ["3 products", "50 keywords", "90-day backfill", "4 deep analysis credits"],
    current: true,
    highlighted: true,
  },
  {
    name: "Agency",
    price: "$299",
    description: "For agencies",
    features: ["Unlimited products", "Unlimited keywords", "Full backfill", "Unlimited analysis"],
    current: false,
  },
]

export default function BillingPage() {
  const { getToken } = useAuthToken()

  // Fetch products to count usage
  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const token = await getToken()
      return api.products.list(token)
    },
  })

  // Fetch credits
  const { data: creditsData, isLoading: creditsLoading } = useQuery({
    queryKey: ["credits"],
    queryFn: async () => {
      const token = await getToken()
      return api.insights.getCredits(token)
    },
  })

  const isLoading = productsLoading || creditsLoading
  const productCount = productsData?.total || 0
  const tier = creditsData?.tier || "indie"

  // Usage limits based on tier
  const limits = {
    indie: { products: 1, keywords: 10 },
    pro: { products: 3, keywords: 50 },
    agency: { products: Infinity, keywords: Infinity },
  }

  const currentLimits = limits[tier as keyof typeof limits] || limits.indie

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription and view usage.
        </p>
      </div>

      {/* Current plan */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Current Plan
              </CardTitle>
              <CardDescription>
                Your current subscription plan and billing details.
              </CardDescription>
            </div>
            <Badge variant="default" className="text-sm">
              {tier.charAt(0).toUpperCase() + tier.slice(1)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-20" />
          ) : (
            <div className="space-y-4">
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold">
                  {tier === "indie" ? "$39" : tier === "pro" ? "$99" : "$299"}
                </span>
                <span className="text-muted-foreground">/month</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Next billing date: February 1, 2026
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Usage */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Usage</CardTitle>
          <CardDescription>
            Your current usage against your plan limits.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Products */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Products</span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {productCount} /{" "}
                    {currentLimits.products === Infinity
                      ? "Unlimited"
                      : currentLimits.products}
                  </span>
                </div>
                {currentLimits.products !== Infinity && (
                  <Progress
                    value={(productCount / currentLimits.products) * 100}
                    className="h-2"
                  />
                )}
              </div>

              {/* Keywords placeholder */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Key className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Keywords</span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    -- /{" "}
                    {currentLimits.keywords === Infinity
                      ? "Unlimited"
                      : currentLimits.keywords}
                  </span>
                </div>
                {currentLimits.keywords !== Infinity && (
                  <Progress value={0} className="h-2" />
                )}
              </div>

              {/* Deep analysis credits */}
              {creditsData && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">
                        Deep Analysis Credits
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {creditsData.is_unlimited
                        ? "Unlimited"
                        : `${creditsData.credits_remaining} / ${creditsData.credits_total}`}
                    </span>
                  </div>
                  {!creditsData.is_unlimited && (
                    <Progress
                      value={
                        (creditsData.credits_remaining /
                          creditsData.credits_total) *
                        100
                      }
                      className="h-2"
                    />
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Available plans */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Available Plans</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const isCurrent = plan.name.toLowerCase() === tier

            return (
              <Card
                key={plan.name}
                className={
                  plan.highlighted ? "border-primary border-2" : ""
                }
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{plan.name}</CardTitle>
                    {isCurrent && <Badge>Current</Badge>}
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">/mo</span>
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <ul className="space-y-2">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2 text-sm">
                        <Check className="h-4 w-4 text-primary" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  {isCurrent ? (
                    <Button variant="outline" className="w-full" disabled>
                      Current Plan
                    </Button>
                  ) : plan.name.toLowerCase() === "agency" ||
                    (plan.name.toLowerCase() === "pro" && tier === "indie") ? (
                    <Button className="w-full">Upgrade</Button>
                  ) : (
                    <Button variant="outline" className="w-full">
                      Downgrade
                    </Button>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Billing info placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Billing Information</CardTitle>
          <CardDescription>
            Manage your payment method and billing address.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Payment integration with Stripe coming soon. For now, all plans are
            available during the beta period.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
