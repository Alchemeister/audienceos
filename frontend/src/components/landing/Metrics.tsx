"use client"

import { motion } from "framer-motion"
import { TrendingUp, Users, Clock } from "lucide-react"

export function Metrics() {
  const metrics = [
    {
      icon: Users,
      value: "47",
      label: "Mentions Found",
      sublabel: "In the last 24 hours",
      gradient: "from-purple-500 to-pink-500",
    },
    {
      icon: TrendingUp,
      value: "12%",
      label: "Conversion Rate",
      sublabel: "From tracked mentions",
      gradient: "from-pink-500 to-orange-500",
    },
    {
      icon: Clock,
      value: "90",
      label: "Day Backfill",
      sublabel: "Historical data included",
      gradient: "from-cyan-500 to-blue-500",
    },
  ]

  return (
    <section className="relative py-32 px-4">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-900/10 to-transparent" />

      <div className="relative z-10 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-white">Real results.</span>
            <br />
            <span className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              Real impact.
            </span>
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            Join hundreds of founders who are finally hearing what their
            audience is saying.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {metrics.map((metric, i) => {
            const Icon = metric.icon
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="relative group"
              >
                <div className="rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8 hover:border-white/20 transition-all duration-300">
                  {/* Icon */}
                  <div
                    className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${metric.gradient} flex items-center justify-center mb-6`}
                  >
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Value with gradient */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 + 0.2, type: "spring" }}
                    className={`text-7xl font-bold mb-4 bg-gradient-to-r ${metric.gradient} bg-clip-text text-transparent`}
                  >
                    {metric.value}
                  </motion.div>

                  {/* Label */}
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {metric.label}
                  </h3>
                  <p className="text-white/60">{metric.sublabel}</p>

                  {/* Green arrow indicator */}
                  <div className="mt-6 flex items-center gap-2 text-green-400">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm font-semibold">Trending up</span>
                  </div>
                </div>

                {/* Glow effect */}
                <div
                  className={`absolute -inset-1 bg-gradient-to-r ${metric.gradient} opacity-0 group-hover:opacity-20 blur-2xl transition-opacity rounded-3xl -z-10`}
                />
              </motion.div>
            )
          })}
        </div>

        {/* Progress bar section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-20 rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8"
        >
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h3 className="text-3xl font-bold text-white mb-3">
                Your audience is out there
              </h3>
              <p className="text-white/60">
                On average, founders discover 47 mentions in their first week
              </p>
            </div>

            {/* Animated progress bar */}
            <div className="space-y-4">
              {[
                { label: "Reddit conversations", value: 85 },
                { label: "Hacker News threads", value: 70 },
                { label: "X mentions", value: 60 },
                { label: "Forum discussions", value: 45 },
              ].map((item, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/80">{item.label}</span>
                    <span className="text-white font-semibold">{item.value}%</span>
                  </div>
                  <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${item.value}%` }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1, duration: 1 }}
                      className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 rounded-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
