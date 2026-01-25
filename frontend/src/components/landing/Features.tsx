"use client"

import { motion } from "framer-motion"
import { MessageSquare, Users, TrendingUp, BarChart3, Bell } from "lucide-react"

export function Features() {
  return (
    <section id="features" className="relative py-32 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              Everything you need
            </span>
            <br />
            <span className="text-white">in one dashboard</span>
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            Stop switching between tabs. Monitor all your channels and engage
            with your audience from a single place.
          </p>
        </motion.div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-[280px]">
          {/* Large card - Feedback Aggregator */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="md:col-span-2 rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8 hover:border-purple-500/50 transition-all duration-300 group overflow-hidden relative"
          >
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Unified Feedback Inbox
              </h3>
              <p className="text-white/60 mb-6">
                All mentions, comments, and messages in one place. Never miss a
                conversation about your product.
              </p>

              {/* Mini dashboard preview */}
              <div className="space-y-2">
                {[
                  { platform: "Reddit", color: "from-orange-500" },
                  { platform: "HN", color: "from-orange-600" },
                  { platform: "X", color: "from-blue-500" },
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + i * 0.1 }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5"
                  >
                    <div
                      className={`w-8 h-8 rounded-lg bg-gradient-to-br ${item.color} to-pink-500 flex-shrink-0`}
                    />
                    <div className="flex-1 h-3 bg-white/10 rounded" />
                    <div className="w-2 h-2 rounded-full bg-green-400" />
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Background glow */}
            <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl group-hover:bg-purple-600/30 transition-colors" />
          </motion.div>

          {/* Medium card - Audience Discovery */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8 hover:border-pink-500/50 transition-all duration-300 group overflow-hidden relative"
          >
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Audience Discovery
              </h3>
              <p className="text-white/60 mb-4">
                AI-powered discovery finds where your audience is talking about
                problems you solve.
              </p>

              {/* Subreddit cards fanning out */}
              <div className="relative h-24">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    initial={{ rotate: 0, y: 0 }}
                    whileInView={{ rotate: i * 5 - 5, y: i * 8 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 + i * 0.1 }}
                    className="absolute left-0 right-0 p-3 rounded-xl bg-gradient-to-br from-pink-500/20 to-orange-500/20 border border-pink-500/30"
                    style={{ zIndex: 3 - i }}
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded bg-orange-500" />
                      <div className="text-white text-sm font-medium">r/SaaS</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="absolute -right-16 -bottom-16 w-48 h-48 bg-pink-600/20 rounded-full blur-3xl group-hover:bg-pink-600/30 transition-colors" />
          </motion.div>

          {/* Medium card - AI Insights */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8 hover:border-cyan-500/50 transition-all duration-300 group overflow-hidden relative"
          >
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">AI Insights</h3>
              <p className="text-white/60 mb-6">
                Sentiment analysis and trend detection help you understand what
                your audience really thinks.
              </p>

              {/* Sentiment chart */}
              <div className="space-y-2">
                {[
                  { label: "Positive", value: 92, color: "bg-green-500" },
                  { label: "Neutral", value: 6, color: "bg-yellow-500" },
                  { label: "Negative", value: 2, color: "bg-red-500" },
                ].map((item, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-white/60">{item.label}</span>
                      <span className="text-white font-semibold">{item.value}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${item.value}%` }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.4 + i * 0.1, duration: 0.8 }}
                        className={`h-full ${item.color}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="absolute -right-16 -bottom-16 w-48 h-48 bg-cyan-600/20 rounded-full blur-3xl group-hover:bg-cyan-600/30 transition-colors" />
          </motion.div>

          {/* Small card - Campaign Tracking */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8 hover:border-orange-500/50 transition-all duration-300 group overflow-hidden relative"
          >
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Campaign Tracking
              </h3>
              <p className="text-white/60 mb-4">
                Track mentions and conversions from every campaign launch.
              </p>

              {/* Conversion metrics */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-white/60 text-sm">Mentions</span>
                  <span className="text-white font-bold text-xl">47</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white/60 text-sm">Clicks</span>
                  <span className="text-white font-bold text-xl">234</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white/60 text-sm">Conversions</span>
                  <span className="text-green-400 font-bold text-xl flex items-center gap-1">
                    28 <span className="text-sm">↑</span>
                  </span>
                </div>
              </div>
            </div>

            <div className="absolute -right-12 -bottom-12 w-40 h-40 bg-orange-600/20 rounded-full blur-3xl group-hover:bg-orange-600/30 transition-colors" />
          </motion.div>

          {/* Small card - Real-time Alerts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/10 p-8 hover:border-purple-500/50 transition-all duration-300 group overflow-hidden relative"
          >
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Instant Alerts</h3>
              <p className="text-white/60 mb-4">
                Get notified the moment someone mentions your product or keywords.
              </p>

              {/* Alert notifications */}
              <div className="space-y-2">
                {[1, 2].map((i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.6 + i * 0.1 }}
                    className="flex items-center gap-2 p-3 rounded-xl bg-purple-500/10 border border-purple-500/30"
                  >
                    <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                    <span className="text-white/80 text-sm">New mention detected</span>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="absolute -right-12 -bottom-12 w-40 h-40 bg-purple-600/20 rounded-full blur-3xl group-hover:bg-purple-600/30 transition-colors" />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
