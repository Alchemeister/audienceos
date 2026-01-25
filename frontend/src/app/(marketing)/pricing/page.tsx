import Link from "next/link"
import { Check, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const tiers = [
  {
    name: "Indie",
    price: "$39",
    description: "For indie hackers and early-stage founders",
    features: {
      products: "1 product",
      keywords: "10 keywords",
      backfill: "2-week historical backfill",
      deepAnalysis: "Not included",
      sentiment: "Basic sentiment analysis",
      reports: "Weekly email reports",
      support: "Community support",
    },
  },
  {
    name: "Pro",
    price: "$99",
    description: "For growing startups",
    features: {
      products: "3 products",
      keywords: "50 keywords",
      backfill: "90-day historical backfill",
      deepAnalysis: "4 credits/month",
      sentiment: "Advanced sentiment analysis",
      reports: "Weekly email reports",
      support: "Priority support",
    },
    highlighted: true,
  },
  {
    name: "Agency",
    price: "$299",
    description: "For agencies and enterprises",
    features: {
      products: "Unlimited products",
      keywords: "Unlimited keywords",
      backfill: "Full historical backfill",
      deepAnalysis: "Unlimited",
      sentiment: "Advanced sentiment analysis",
      reports: "White-label reports",
      support: "Dedicated support",
    },
  },
]

const allFeatures = [
  { name: "Real-time feedback collection", indie: true, pro: true, agency: true },
  { name: "Reddit monitoring", indie: true, pro: true, agency: true },
  { name: "Hacker News monitoring", indie: true, pro: true, agency: true },
  { name: "X monitoring", indie: false, pro: true, agency: true },
  { name: "Email feedback widget", indie: true, pro: true, agency: true },
  { name: "Audience research", indie: true, pro: true, agency: true },
  { name: "Campaign management", indie: true, pro: true, agency: true },
  { name: "Link tracking", indie: true, pro: true, agency: true },
  { name: "AI content generation", indie: true, pro: true, agency: true },
  { name: "Theme clustering", indie: false, pro: true, agency: true },
  { name: "Churn risk analysis", indie: false, pro: true, agency: true },
  { name: "Competitor intelligence", indie: false, pro: true, agency: true },
  { name: "API access", indie: false, pro: false, agency: true },
  { name: "Custom integrations", indie: false, pro: false, agency: true },
]

export default function PricingPage() {
  return (
    <div className="py-20">
      <div className="container px-4 md:px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl">
            Simple, Transparent Pricing
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include a 14-day free
            trial with no credit card required.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-20">
          {tiers.map((tier) => (
            <Card
              key={tier.name}
              className={tier.highlighted ? "border-primary border-2 relative" : ""}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                    MOST POPULAR
                  </span>
                </div>
              )}
              <CardHeader className="pt-8">
                <CardTitle className="text-2xl">{tier.name}</CardTitle>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className="text-5xl font-bold">{tier.price}</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <CardDescription className="mt-2">
                  {tier.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/sign-up">
                  <Button
                    className="w-full mb-6"
                    variant={tier.highlighted ? "default" : "outline"}
                    size="lg"
                  >
                    Start Free Trial
                  </Button>
                </Link>
                <ul className="space-y-3">
                  {Object.entries(tier.features).map(([key, value]) => (
                    <li key={key} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-sm">{value}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Feature Comparison Table */}
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">
            Feature Comparison
          </h2>
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[40%]">Feature</TableHead>
                  <TableHead className="text-center">Indie</TableHead>
                  <TableHead className="text-center bg-primary/5">Pro</TableHead>
                  <TableHead className="text-center">Agency</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allFeatures.map((feature) => (
                  <TableRow key={feature.name}>
                    <TableCell className="font-medium">{feature.name}</TableCell>
                    <TableCell className="text-center">
                      {feature.indie ? (
                        <Check className="h-5 w-5 text-primary mx-auto" />
                      ) : (
                        <X className="h-5 w-5 text-muted-foreground mx-auto" />
                      )}
                    </TableCell>
                    <TableCell className="text-center bg-primary/5">
                      {feature.pro ? (
                        <Check className="h-5 w-5 text-primary mx-auto" />
                      ) : (
                        <X className="h-5 w-5 text-muted-foreground mx-auto" />
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {feature.agency ? (
                        <Check className="h-5 w-5 text-primary mx-auto" />
                      ) : (
                        <X className="h-5 w-5 text-muted-foreground mx-auto" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto mt-20">
          <h2 className="text-2xl font-bold text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">
                Can I switch plans at any time?
              </h3>
              <p className="text-muted-foreground text-sm">
                Yes, you can upgrade or downgrade your plan at any time. Changes
                take effect immediately, and we&apos;ll prorate your billing.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                What happens after the free trial?
              </h3>
              <p className="text-muted-foreground text-sm">
                After your 14-day trial, you&apos;ll need to choose a paid plan to
                continue using AudienceOS. Your data will be preserved.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                What is &quot;historical backfill&quot;?
              </h3>
              <p className="text-muted-foreground text-sm">
                When you add a product, we search for existing mentions across the
                web and import them into your dashboard. Indie gets 2 weeks, Pro
                gets 90 days, and Agency gets full history.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                What are deep analysis credits?
              </h3>
              <p className="text-muted-foreground text-sm">
                Deep analysis uses advanced AI to provide detailed churn analysis,
                competitor intelligence, and content strategy recommendations.
                Each analysis consumes one credit.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-muted-foreground text-sm">
                We offer a 30-day money-back guarantee. If you&apos;re not satisfied
                with AudienceOS, contact us for a full refund.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
