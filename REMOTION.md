# Remotion - Video Marketing for AudienceOS

## What is Remotion?

Remotion is a framework for creating videos programmatically using React. Instead of editing videos in Premiere or After Effects, you write React components that render as video frames. This gives you:

- **Version control** - Your videos are code, so they live in git
- **Reusability** - Build a template once, swap data to create variations
- **Iteration speed** - Change copy, colors, animations as fast as you change code
- **Data-driven content** - Pull real stats, screenshots, or API data into videos

## Why Use It for AudienceOS Marketing?

As a developer-founded product, you can:

1. Create product demos that actually show real UI (not mockups)
2. Iterate on ad creatives without hiring a video editor
3. A/B test video variations by changing props
4. Generate multiple versions for different platforms (Twitter, LinkedIn, YouTube)

## Installation

```bash
npx create-video@latest audienceos-videos
cd audienceos-videos
npm start
```

This spins up a dev server with a timeline-based preview at `localhost:3000`.

## Project Structure

```
audienceos-videos/
├── src/
│   ├── compositions/        # Each video is a "composition"
│   │   ├── ProductDemo.tsx
│   │   ├── ExplainerVideo.tsx
│   │   └── AdCreative.tsx
│   ├── components/          # Reusable animated elements
│   │   ├── Logo.tsx
│   │   ├── FeatureCard.tsx
│   │   └── StatCounter.tsx
│   └── Root.tsx             # Register all compositions here
├── public/                  # Static assets (screenshots, images)
└── remotion.config.ts
```

## Core Concepts

### Compositions

A composition defines a video's dimensions, duration, and frame rate:

```tsx
import { Composition } from 'remotion';
import { ProductDemo } from './compositions/ProductDemo';

export const RemotionRoot = () => {
  return (
    <Composition
      id="ProductDemo"
      component={ProductDemo}
      durationInFrames={300}  // 10 seconds at 30fps
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

### useCurrentFrame

The core hook — tells you which frame is rendering so you can animate:

```tsx
import { useCurrentFrame, useVideoConfig } from 'remotion';

export const FadeInText = ({ text }: { text: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in over 0.5 seconds
  const opacity = Math.min(1, frame / (fps * 0.5));

  return <h1 style={{ opacity }}>{text}</h1>;
};
```

### Sequences

Control when elements appear:

```tsx
import { Sequence } from 'remotion';

export const ExplainerVideo = () => {
  return (
    <>
      <Sequence from={0} durationInFrames={90}>
        <TitleCard text="Finding your audience is hard" />
      </Sequence>
      <Sequence from={90} durationInFrames={90}>
        <ProblemStatement />
      </Sequence>
      <Sequence from={180} durationInFrames={120}>
        <ProductDemo />
      </Sequence>
    </>
  );
};
```

### Spring Animations

Remotion has physics-based springs for natural motion:

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const BouncyLogo = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 100 }
  });

  return (
    <img
      src="/logo.png"
      style={{ transform: `scale(${scale})` }}
    />
  );
};
```

## Rendering

### Local Render

```bash
npx remotion render src/index.ts ProductDemo out/product-demo.mp4
```

### Remotion Lambda (Cloud Rendering)

For faster renders or batch processing:

```bash
npx remotion lambda render --function-name=remotion-render ProductDemo
```

## Video Ideas for AudienceOS

### 1. Problem/Solution Ad (30 seconds)

**Hook (0-5s):** "You're posting content but have no idea if the right people see it."

**Problem (5-15s):** Show frustrated founder posting to void, zero engagement animations

**Solution (15-25s):** AudienceOS dashboard populating with real subreddits, audience data

**CTA (25-30s):** "Find your audience. AudienceOS.com"

### 2. Product Demo (60 seconds)

**Intro (0-10s):** Logo animation, tagline

**Feature 1 (10-25s):** Marketing Scout - show subreddit discovery UI

**Feature 2 (25-40s):** Feedback Aggregator - show mentions flowing in from multiple sources

**Feature 3 (40-50s):** AI insights - show sentiment analysis, actionable recommendations

**CTA (50-60s):** Pricing tiers, call to action

### 3. Social Proof Short (15 seconds)

Animated stats:
- "47 mentions found in first 24 hours"
- "12% conversion from r/SaaS"
- Counter showing mentions accumulating

---

## Prompt for AI-Assisted Video Scripting

Use this prompt with Claude to generate video scripts:

```
You are a video marketing scriptwriter for AudienceOS, a B2B SaaS that helps founders find their audience and aggregate feedback.

Target audience: Indie hackers, solo founders, small startup teams
Tone: Direct, no-BS, empathetic to founder struggles
Product positioning: SparkToro + Canny + Brand24 replacement

Key value props:
1. Marketing Scout: Find exactly which subreddits/communities your audience uses
2. Feedback Aggregator: All mentions from Reddit/Twitter/HN in one bucket
3. AI Insights: Patterns and actionable recommendations from aggregated feedback

Create a [VIDEO LENGTH] second video script for [PLATFORM].

Format:
- Timestamp
- Visual description (what's on screen)
- Voiceover/text
- Animation notes

The video should [GOAL: introduce the product / highlight a specific feature / address a pain point / show social proof].
```

---

## Resources

- [Remotion Docs](https://www.remotion.dev/docs/)
- [Remotion GitHub](https://github.com/remotion-dev/remotion)
- [Example Videos](https://www.remotion.dev/showcase)
- [Template Gallery](https://www.remotion.dev/templates)
