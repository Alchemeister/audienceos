"use client"

import { motion } from "framer-motion"
import { Menu } from "lucide-react"
import { useState } from "react"
import Link from "next/link"

export function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 px-4 py-6"
    >
      <div className="max-w-7xl mx-auto">
        <div className="rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500" />
              <span className="text-white font-bold text-xl">AudienceOS</span>
            </Link>

            {/* Desktop navigation */}
            <div className="hidden md:flex items-center gap-8">
              <a
                href="#features"
                className="text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Features
              </a>
              <a
                href="#pricing"
                className="text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Pricing
              </a>
              <a
                href="#"
                className="text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Docs
              </a>
              <a
                href="#"
                className="text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Blog
              </a>
            </div>

            {/* CTA buttons */}
            <div className="hidden md:flex items-center gap-4">
              <Link
                href="/sign-in"
                className="px-6 py-2 text-white/80 hover:text-white text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                className="px-6 py-2 rounded-xl bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 text-white text-sm font-semibold hover:shadow-lg hover:shadow-purple-500/30 transition-all"
              >
                Get Started
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-white/80 hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>

          {/* Mobile menu */}
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="md:hidden mt-6 pt-6 border-t border-white/10 space-y-4"
            >
              <a
                href="#features"
                className="block text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Features
              </a>
              <a
                href="#pricing"
                className="block text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Pricing
              </a>
              <a
                href="#"
                className="block text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Docs
              </a>
              <a
                href="#"
                className="block text-white/80 hover:text-white transition-colors text-sm font-medium"
              >
                Blog
              </a>
              <div className="pt-4 space-y-2">
                <Link
                  href="/sign-in"
                  className="block w-full px-6 py-2 text-white/80 hover:text-white text-sm font-medium transition-colors text-left"
                >
                  Sign In
                </Link>
                <Link
                  href="/sign-up"
                  className="block w-full px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 text-white text-sm font-semibold text-center"
                >
                  Get Started
                </Link>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.nav>
  )
}
