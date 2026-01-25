"use client"

import { motion } from "framer-motion"
import { Check, Sparkles } from "lucide-react"
import Link from "next/link"

export function Pricing() {
  const plans = [
    {
      name: "Indie",
      price: "$39",
      description: "For solo founders getting started",
      features: [
        "Up to 5 tracked keywords",
        "3 platform integrations",
        "Basic sentiment analysis",
        "Email alerts",
        "30-day history",
        "Community support",
      ],
      highlighted: false,
    },
    {
      name: "Pro",
      price: "$99",
      description: "For growing teams and products",
      features: [
        "Unlimited keywords",
        "All platform integrations",
        "Advanced AI insights",
        "Real-time alerts",
        "90-day history backfill",
        "Priority support",
        "Custom reports",
        "API access",
      ],
      highlighted: true,
      badge: "Most Popular",
    },
    {
      name: "Agency",
      price: "$299",
      description: "For agencies managing multiple clients",
      features: [
        "Everything in Pro",
        "Multi-workspace support",
        "White-label reports",
        "Team collaboration",
        "Unlimited history",
        "Dedicated support",
        "Custom integrations",
        "SLA guarantee",
      ],
      highlighted: false,
    },
  ]

  return (
    <section id="pricing" className="relative py-32 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-white">Simple pricing.</span>
            <br />
            <span className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              Serious value.
            </span>
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include a 14-day
            free trial.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={`relative ${plan.highlighted ? "md:scale-105 md:-my-4" : ""}`}
            >
              {/* Highlighted border for Pro plan */}
              {plan.highlighted && (
                <div className="absolute -inset-[1px] bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 rounded-3xl blur-sm" />
              )}

              <div
                className={`relative rounded-3xl backdrop-blur-sm p-8 h-full flex flex-col ${
                  plan.highlighted
                    ? "bg-gradient-to-br from-white/15 to-white/10 border border-white/20"
                    : "bg-gradient-to-br from-white/10 to-white/5 border border-white/10"
                }`}
              >
                {/* Badge for Pro plan */}
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-semibold">
                      <Sparkles className="w-4 h-4" />
                      {plan.badge}
                    </div>
                  </div>
                )}

                {/* Plan header */}
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-white/60 text-sm mb-4">{plan.description}</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-6xl font-bold text-white">{plan.price}</span>
                    <span className="text-white/60">/month</span>
                  </div>
                </div>

                {/* Features list */}
                <div className="flex-1 space-y-4 mb-8">
                  {plan.features.map((feature, j) => (
                    <div key={j} className="flex items-start gap-3">
                      <div
                        className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          plan.highlighted
                            ? "bg-gradient-to-r from-purple-500 to-pink-500"
                            : "bg-white/10"
                        }`}
                      >
                        <Check className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-white/80 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* CTA button */}
                <Link
                  href="/sign-up"
                  className={`w-full py-4 rounded-2xl font-semibold transition-all duration-300 text-center block ${
                    plan.highlighted
                      ? "bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 text-white hover:shadow-2xl hover:shadow-purple-500/50 hover:scale-105"
                      : "bg-white/10 text-white border border-white/20 hover:bg-white/15"
                  }`}
                >
                  {plan.highlighted ? "Start Free Trial" : "Get Started"}
                </Link>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Comparison note */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <p className="text-white/40 text-sm">
            All plans include 14-day free trial • No credit card required •
            Cancel anytime
          </p>
        </motion.div>
      </div>
    </section>
  )
}
