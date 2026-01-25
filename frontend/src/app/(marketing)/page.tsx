"use client"

import {
  Navigation,
  Hero,
  SocialProof,
  Features,
  Metrics,
  Pricing,
  CTASection,
  Footer,
} from "@/components/landing"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white overflow-x-hidden">
      {/* Background grid pattern */}
      <div
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle, white 1px, transparent 1px)`,
          backgroundSize: "32px 32px",
        }}
      />

      <Navigation />
      <Hero />
      <SocialProof />
      <Features />
      <Metrics />
      <Pricing />
      <CTASection />
      <Footer />
    </div>
  )
}
