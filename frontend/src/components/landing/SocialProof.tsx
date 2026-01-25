"use client"

import { motion } from "framer-motion"

export function SocialProof() {
  const logos = [
    "Reddit",
    "Hacker News",
    "Product Hunt",
    "X / Twitter",
    "Discord",
    "Slack",
    "GitHub",
    "LinkedIn",
  ]

  return (
    <section className="relative py-16 border-y border-white/5 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <p className="text-white/40 text-sm uppercase tracking-wider">
            Trusted by 500+ founders
          </p>
        </motion.div>

        {/* Infinite scroll animation */}
        <div className="relative flex overflow-hidden">
          <motion.div
            animate={{
              x: [0, -1000],
            }}
            transition={{
              x: {
                repeat: Infinity,
                repeatType: "loop",
                duration: 20,
                ease: "linear",
              },
            }}
            className="flex gap-12 items-center whitespace-nowrap"
          >
            {[...logos, ...logos, ...logos].map((logo, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-white/30 hover:text-white/60 transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-xs font-bold">
                  {logo[0]}
                </div>
                <span className="text-sm font-medium">{logo}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
