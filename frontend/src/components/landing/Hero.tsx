"use client"

import { ArrowRight, Play } from "lucide-react"
import { motion } from "framer-motion"
import Link from "next/link"

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden px-4 pt-24">
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/4 -left-48 w-96 h-96 rounded-full bg-gradient-to-r from-purple-600/30 to-pink-600/30 blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute bottom-1/4 -right-48 w-96 h-96 rounded-full bg-gradient-to-l from-orange-600/30 to-pink-600/30 blur-3xl"
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto text-center">
        {/* Floating badges */}
        <div className="relative mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="absolute -left-20 top-0 hidden xl:block"
          >
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
              <div className="w-6 h-6 rounded-full bg-orange-500 flex items-center justify-center text-xs font-bold text-white">
                r/
              </div>
              <span className="text-sm text-white/80">Reddit</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="absolute -right-20 top-20 hidden xl:block"
          >
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
              <div className="w-6 h-6 rounded-full bg-orange-500 flex items-center justify-center text-xs font-bold text-white">
                Y
              </div>
              <span className="text-sm text-white/80">Hacker News</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="absolute -left-32 bottom-0 hidden xl:block"
          >
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
              <div className="w-6 h-6 rounded-full bg-black flex items-center justify-center text-xs text-white font-bold">
                X
              </div>
              <span className="text-sm text-white/80">X / Twitter</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="absolute -right-32 bottom-10 hidden xl:block"
          >
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
              <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-xs text-white">
                @
              </div>
              <span className="text-sm text-white/80">Email</span>
            </div>
          </motion.div>
        </div>

        {/* Headline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 tracking-tight">
            <span className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              Find Your Audience.
            </span>
            <br />
            <span className="text-white">Hear Their Feedback.</span>
          </h1>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-xl md:text-2xl text-white/60 mb-12 max-w-3xl mx-auto"
        >
          Stop losing customers in the noise. AudienceOS discovers where your
          audience hangs out online and aggregates every mention into one
          powerful dashboard.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16"
        >
          <Link
            href="/sign-up"
            className="group relative px-8 py-4 rounded-2xl bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 text-white font-semibold text-lg hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105"
          >
            Start Free Trial
            <ArrowRight className="inline-block ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <button className="px-8 py-4 rounded-2xl border border-white/20 text-white font-semibold text-lg backdrop-blur-sm hover:bg-white/5 transition-all duration-300 flex items-center gap-2">
            <Play className="w-5 h-5" />
            See Demo
          </button>
        </motion.div>

        {/* Hero visual - Dashboard mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.6 }}
          className="relative max-w-5xl mx-auto"
        >
          <div className="relative rounded-3xl overflow-hidden border border-white/10 bg-white/5 backdrop-blur-sm p-1">
            <div className="rounded-2xl overflow-hidden bg-[#0A0A0F]">
              {/* Dashboard mockup */}
              <div className="p-8 space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500" />
                    <div>
                      <div className="text-white font-semibold">AudienceOS</div>
                      <div className="text-white/40 text-sm">Dashboard</div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/50" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                    <div className="w-3 h-3 rounded-full bg-green-500/50" />
                  </div>
                </div>

                {/* Cards grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Mentions card */}
                  <div className="rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-white/60 text-sm">New Mentions</span>
                      <div className="px-2 py-1 rounded-full bg-cyan-500/20 text-cyan-400 text-xs font-semibold">
                        +12
                      </div>
                    </div>
                    <div className="text-4xl font-bold text-white mb-2">47</div>
                    <div className="text-white/40 text-sm flex items-center gap-1">
                      <span className="text-green-400">↑ 24%</span> vs last week
                    </div>
                  </div>

                  {/* Sentiment card */}
                  <div className="rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-white/60 text-sm">Avg Sentiment</span>
                      <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    </div>
                    <div className="text-4xl font-bold text-white mb-2">92%</div>
                    <div className="text-white/40 text-sm">Positive feedback</div>
                  </div>

                  {/* Conversion card */}
                  <div className="rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-white/60 text-sm">Conversion</span>
                      <div className="px-2 py-1 rounded-full bg-purple-500/20 text-purple-400 text-xs font-semibold">
                        ⚡
                      </div>
                    </div>
                    <div className="text-4xl font-bold text-white mb-2">12%</div>
                    <div className="text-white/40 text-sm flex items-center gap-1">
                      <span className="text-green-400">↑ 3.2%</span> this month
                    </div>
                  </div>
                </div>

                {/* Recent mentions list */}
                <div className="space-y-3">
                  <div className="text-white/60 text-sm font-medium">
                    Recent Mentions
                  </div>
                  {[
                    { platform: "Reddit", text: "Just tried AudienceOS, game changer...", time: "2m ago" },
                    { platform: "HN", text: "Looking for tools to track mentions...", time: "15m ago" },
                    { platform: "X", text: "AudienceOS helped me find my first users", time: "1h ago" },
                  ].map((mention, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1 + i * 0.1 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
                    >
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-pink-500 flex items-center justify-center text-xs font-bold text-white">
                        {mention.platform[0]}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-white text-sm truncate">{mention.text}</div>
                        <div className="text-white/40 text-xs">
                          {mention.platform} • {mention.time}
                        </div>
                      </div>
                      <div className="w-2 h-2 rounded-full bg-cyan-400" />
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Glow effect */}
          <div className="absolute -inset-4 bg-gradient-to-r from-purple-600/20 via-pink-600/20 to-orange-600/20 blur-3xl -z-10 opacity-50" />
        </motion.div>
      </div>
    </section>
  )
}
