# AudienceOS Pricing & AI Cost Analysis

## AI Model Pricing Comparison (January 2026)

### Budget Tier Models (For Filtering & Classification)

| Provider | Model | Input/MTok | Output/MTok | MMLU | Best For |
|----------|-------|------------|-------------|------|----------|
| Mistral | Small 3.2 | $0.03 | $0.11 | 81% | Basic classification (fastest) |
| Groq | Llama 3.1 8B | $0.05 | $0.08 | 73% | Ultra-low cost filtering |
| DeepSeek | V3 (cached) | $0.028 | $0.42 | 88.5% | **Best value + quality** |
| DeepSeek | V3 | $0.28 | $0.42 | 88.5% | High quality cheap |
| Google | Gemini Flash | $0.10 | $0.40 | 78% | Speed (200+ tok/s) |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | 82% | Reliable, low hallucination |
| Anthropic | Haiku 3.5 | $0.80 | $4.00 | 75% | Quality fallback |

### Premium Tier Models (For Analysis & Generation)

| Provider | Model | Input/MTok | Output/MTok | MMLU | Best For |
|----------|-------|------------|-------------|------|----------|
| Mistral | Medium 3.1 | $0.40 | $2.00 | 84% | Budget premium |
| Groq | Llama 3.3 70B | $0.59 | $0.79 | 86% | Fast + capable |
| OpenAI | GPT-4o | $2.50 | $10.00 | 88% | Reliable reasoning |
| Anthropic | Sonnet 4.5 | $3.00 | $15.00 | 85% | **Best writing quality** |
| Google | Gemini 2.5 Pro | $1.25 | $10.00 | 89% | Large context (1M) |
| OpenAI | GPT-4-turbo | $5.00 | $15.00 | 86% | Established, reliable |

---

## Token Estimates per Operation

### Cheap Model Operations (DeepSeek)

| Operation | Input Tokens | Output Tokens | Cost/Op |
|-----------|--------------|---------------|---------|
| Relevance Filter | ~500 | ~100 | $0.000182 |
| Basic Classification | ~400 | ~100 | $0.000154 |
| **Combined Filter+Classify** | ~900 | ~200 | **$0.000336** |

### Expensive Model Operations (Claude Sonnet)

| Operation | Input Tokens | Output Tokens | Cost/Op |
|-----------|--------------|---------------|---------|
| Sentiment Analysis (detailed) | ~800 | ~300 | $0.0069 |
| Audience Research | ~1,000 | ~1,500 | $0.0255 |
| Content Generation (3 posts) | ~1,200 | ~2,000 | $0.0336 |
| Weekly Report | ~3,000 | ~2,500 | $0.0465 |
| Theme Clustering | ~2,000 | ~1,500 | $0.0285 |
| Deep Analysis | ~5,000 | ~4,000 | $0.0750 |
| Keyword Discovery | ~800 | ~1,200 | $0.0204 |

---

## Tier Cost Calculations

### Processing Flow
```
Raw mentions → Cheap filter (15% pass) → Cheap classify → Store
                                                           ↓
Weekly: Expensive batch insight → Report
```

### Indie Tier - $39/month

| Feature | Usage | Model | Calculation | Cost |
|---------|-------|-------|-------------|------|
| Raw mentions scanned | ~3,333 | DeepSeek | 3333 × $0.000182 | $0.61 |
| Classification | 500 | DeepSeek | 500 × $0.000154 | $0.08 |
| Keyword Discovery | 1 (initial) | Sonnet | 1 × $0.0204 | $0.02 |
| Audience Research | 10 | Sonnet | 10 × $0.0255 | $0.26 |
| Content Generation | 50 | Sonnet | 50 × $0.0336 | $1.68 |
| Weekly Reports | 4 | Sonnet | 4 × $0.0465 | $0.19 |
| Theme Clustering | 4 | Sonnet | 4 × $0.0285 | $0.11 |
| **Total AI Cost** | | | | **$2.95** |
| **Revenue** | | | | **$39.00** |
| **Margin** | | | | **92.4%** ✅ |

### Pro Tier - $99/month

| Feature | Usage | Model | Calculation | Cost |
|---------|-------|-------|-------------|------|
| Raw mentions scanned | ~33,333 | DeepSeek | 33333 × $0.000182 | $6.07 |
| Classification | 5,000 | DeepSeek | 5000 × $0.000154 | $0.77 |
| Keyword Discovery | 3 (per product) | Sonnet | 3 × $0.0204 | $0.06 |
| Audience Research | 30 | Sonnet | 30 × $0.0255 | $0.77 |
| Content Generation | 150 | Sonnet | 150 × $0.0336 | $5.04 |
| Weekly Reports | 12 (3 products) | Sonnet | 12 × $0.0465 | $0.56 |
| Theme Clustering | 12 | Sonnet | 12 × $0.0285 | $0.34 |
| Deep Analysis | 4 credits | Sonnet | 4 × $0.0750 | $0.30 |
| **Total AI Cost** | | | | **$13.91** |
| **Revenue** | | | | **$99.00** |
| **Margin** | | | | **86.0%** ✅ |

### Agency Tier - $299/month

Assuming average of 7 products with heavy usage:

| Feature | Usage | Model | Calculation | Cost |
|---------|-------|-------|-------------|------|
| Raw mentions scanned | ~100,000 | DeepSeek | 100000 × $0.000182 | $18.20 |
| Classification | 15,000 | DeepSeek | 15000 × $0.000154 | $2.31 |
| Keyword Discovery | 7 | Sonnet | 7 × $0.0204 | $0.14 |
| Audience Research | 70 | Sonnet | 70 × $0.0255 | $1.79 |
| Content Generation | 350 | Sonnet | 350 × $0.0336 | $11.76 |
| Weekly Reports | 28 (7 products) | Sonnet | 28 × $0.0465 | $1.30 |
| Theme Clustering | 28 | Sonnet | 28 × $0.0285 | $0.80 |
| Deep Analysis | 20 | Sonnet | 20 × $0.0750 | $1.50 |
| **Total AI Cost** | | | | **$37.80** |
| **Revenue** | | | | **$299.00** |
| **Margin** | | | | **87.4%** ✅ |

---

## Summary Table

| Tier | Price | Est. AI Cost | Margin | Docs Target |
|------|-------|--------------|--------|-------------|
| Indie | $39 | $2.95 | 92.4% | 85%+ ✅ |
| Pro | $99 | $13.91 | 86.0% | 80%+ ✅ |
| Agency | $299 | $37.80 | 87.4% | 85%+ ✅ |

---

## Cost Comparison: DeepSeek vs Claude Haiku

If DeepSeek is unavailable and we fallback to Claude Haiku:

| Operation | DeepSeek Cost | Haiku Cost | Increase |
|-----------|---------------|------------|----------|
| Filter (500 in / 100 out) | $0.000182 | $0.000800 | 4.4x |
| Classify (400 in / 100 out) | $0.000154 | $0.000720 | 4.7x |

**Impact on Margins (Haiku fallback):**

| Tier | DeepSeek Margin | Haiku Margin | Difference |
|------|-----------------|--------------|------------|
| Indie | 92.4% | 90.6% | -1.8% |
| Pro | 86.0% | 79.5% | -6.5% |
| Agency | 87.4% | 80.1% | -7.3% |

Haiku fallback is still profitable but reduces margins by 2-7%.

---

## Critical Architecture Considerations

### Current Implementation Risk ⚠️

The current `router.py` routes `analyze_sentiment()` through the **expensive** model (Sonnet) for every feedback item. If used on all 500-5,000 items:

| Tier | Items | Cost at $0.0069/item | Impact |
|------|-------|---------------------|--------|
| Indie | 500 | $3.45 | Margin drops to 84% |
| Pro | 5,000 | $34.50 | Margin drops to 51% ⚠️ |
| Agency | 15,000 | $103.50 | Margin drops to 53% ⚠️ |

### Recommended Fix

1. Use **cheap model** for initial classification (sentiment, category, urgency)
2. Use **expensive model** only for:
   - Flagged items needing nuanced analysis (10% of items)
   - Batch insight generation
   - Content creation
   - Deep analysis credits

This is already the documented architecture - just ensure the code follows it.

---

## Break-Even Analysis

Minimum users needed to cover fixed costs (assuming $500/mo server costs):

| Tier | Price | AI Cost | Contribution | Users to Break Even |
|------|-------|---------|--------------|---------------------|
| Indie | $39 | $2.95 | $36.05 | 14 users |
| Pro | $99 | $13.91 | $85.09 | 6 users |
| Agency | $299 | $37.80 | $261.20 | 2 users |

---

## Recommendations

1. **Pricing is validated** - All tiers exceed target margins with proper architecture
2. **Monitor DeepSeek availability** - Have Haiku fallback ready, margins still work
3. **Enforce cheap model for bulk ops** - Don't use Sonnet for every sentiment analysis
4. **Consider usage-based overage** - Pro users hitting 10K+ feedback items should pay extra
5. **Cache aggressively** - DeepSeek cache hits are 10x cheaper ($0.028 vs $0.28)

---

## AI Provider Pairing Comparison

### Option 1: DeepSeek + Claude Sonnet (RECOMMENDED)
**Cheap:** DeepSeek V3 | **Premium:** Claude Sonnet 4.5

| Metric | Score | Notes |
|--------|-------|-------|
| Cost Efficiency | ⭐⭐⭐⭐⭐ | **With caching: 58% cheaper than GPT-4o-mini** |
| Writing Quality | ⭐⭐⭐⭐⭐ | Claude best-in-class for content |
| Classification | ⭐⭐⭐⭐⭐ | DeepSeek **88.5% MMLU** (best in class) |
| Reliability | ⭐⭐⭐⭐ | DeepSeek newer, less track record |
| Latency | ⭐⭐⭐ | DeepSeek has higher first-token latency (7s) |

**Cost Breakdown (with aggressive caching at 80% hit rate):**
- Filter (cached): 500 × $0.028 + 100 × $0.42 = $0.000056/op
- Filter (no cache): 500 × $0.28 + 100 × $0.42 = $0.000182/op
- **Blended (80% cache):** ~$0.000081/op

**Pro Tier Cost:** $10.50/mo (with caching) | **Margin:** 89%

**Verdict:** Best quality + cheapest with caching. Use for batch processing.

---

### Option 2: Mistral Small + GPT-4o
**Cheap:** Mistral Small 3.2 | **Premium:** GPT-4o

| Metric | Score | Notes |
|--------|-------|-------|
| Cost Efficiency | ⭐⭐⭐⭐ | Mistral cheapest, GPT-4o mid-range |
| Writing Quality | ⭐⭐⭐⭐ | GPT-4o excellent but less refined than Claude |
| Classification | ⭐⭐⭐⭐ | Mistral 81% MMLU (solid) |
| Reliability | ⭐⭐⭐⭐⭐ | Both established providers |
| Latency | ⭐⭐⭐⭐⭐ | Mistral fastest first-token (0.3s) |

**Cost Calculation (Pro Tier):**
- Filtering: 33,333 × ($0.03×500 + $0.11×100)/1M = $0.87
- Classification: 5,000 × $0.000088 = $0.44
- Premium ops: ~$22.50 (GPT-4o more expensive)
- **Total:** ~$23.81/mo | **Margin:** 76%

**Verdict:** Good reliability, but GPT-4o premium costs hurt margins.

---

### Option 3: Gemini Flash + Gemini Pro
**Cheap:** Gemini 2.0 Flash | **Premium:** Gemini 2.5 Pro

| Metric | Score | Notes |
|--------|-------|-------|
| Cost Efficiency | ⭐⭐⭐⭐⭐ | Google's aggressive pricing |
| Writing Quality | ⭐⭐⭐⭐ | Good but less refined tone |
| Classification | ⭐⭐⭐⭐ | Flash 78% MMLU (adequate) |
| Reliability | ⭐⭐⭐⭐ | Google infrastructure |
| Latency | ⭐⭐⭐⭐⭐ | Flash 200+ tok/s (fastest) |
| Context | ⭐⭐⭐⭐⭐ | 1M token context for batch analysis |

**Cost Calculation (Pro Tier):**
- Filtering: 33,333 × ($0.10×500 + $0.40×100)/1M = $3.00
- Classification: 5,000 × $0.000090 = $0.45
- Premium ops: ~$18.00 (Gemini Pro competitive)
- **Total:** ~$21.45/mo | **Margin:** 78%

**Verdict:** Good for speed-critical applications. 1M context great for batch analysis.

---

### Option 4: GPT-4o-mini + Claude Sonnet
**Cheap:** GPT-4o-mini | **Premium:** Claude Sonnet 4.5

| Metric | Score | Notes |
|--------|-------|-------|
| Cost Efficiency | ⭐⭐⭐⭐ | Mini affordable, Claude premium |
| Writing Quality | ⭐⭐⭐⭐⭐ | Best content from Claude |
| Classification | ⭐⭐⭐⭐⭐ | Mini 82% MMLU, low hallucination |
| Reliability | ⭐⭐⭐⭐⭐ | Both industry leaders |
| Latency | ⭐⭐⭐⭐ | 15M tok/min throughput |

**Cost Calculation (Pro Tier):**
- Filtering: 33,333 × ($0.15×500 + $0.60×100)/1M = $4.50
- Classification: 5,000 × $0.000135 = $0.68
- Premium ops: ~$7.00 (Claude Sonnet)
- **Total:** ~$12.18/mo | **Margin:** 88%

**Verdict:** Most reliable combination. Slightly more expensive filtering but excellent quality.

---

### Option 5: Groq Llama + Claude Sonnet
**Cheap:** Groq Llama 3.1 8B | **Premium:** Claude Sonnet 4.5

| Metric | Score | Notes |
|--------|-------|-------|
| Cost Efficiency | ⭐⭐⭐⭐⭐ | Groq ultra-cheap |
| Writing Quality | ⭐⭐⭐⭐⭐ | Claude for premium |
| Classification | ⭐⭐⭐ | Llama 8B 73% MMLU (lower) |
| Reliability | ⭐⭐⭐ | Groq newer, capacity limits |
| Latency | ⭐⭐⭐⭐⭐ | Groq is fastest inference |

**Cost Calculation (Pro Tier):**
- Filtering: 33,333 × ($0.05×500 + $0.08×100)/1M = $1.10
- Classification: 5,000 × $0.000033 = $0.17
- Premium ops: ~$7.00 (Claude Sonnet)
- **Total:** ~$8.27/mo | **Margin:** 92%

**Verdict:** Highest margins but Llama 8B quality may miss nuanced classifications.

---

## Pairing Comparison Summary

| Pairing | Cheap | Premium | Pro Cost | Margin | Quality | Reliability |
|---------|-------|---------|----------|--------|---------|-------------|
| **RECOMMENDED** | DeepSeek V3 (cached) | Claude Sonnet | **$10.50** | **89%** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| DeepSeek (no cache) | DeepSeek V3 | Claude Sonnet | $13.91 | 86% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Reliability Focus | GPT-4o-mini | Claude Sonnet | $12.18 | 88% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Option 3 | Gemini Flash | Gemini Pro | $21.45 | 78% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Option 4 | Mistral Small | GPT-4o | $23.81 | 76% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Budget Max | Groq Llama 8B | Claude Sonnet | $8.27 | 92% | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Final Recommendation

### Primary: DeepSeek + Claude (RECOMMENDED)
- **Best quality**: DeepSeek's 88.5% MMLU is better than GPT-4o-mini's 82%
- **Best cost with caching**: $0.000056/op (58% cheaper than GPT-4o-mini)
- Claude's writing quality unmatched for content generation
- Set `AI_CHEAP_PROVIDER=deepseek` in .env

### Reliability Fallback: GPT-4o-mini + Claude
- Most reliable combination (OpenAI + Anthropic)
- Faster first-token latency (0.6s vs 7s)
- Use for real-time user-facing operations
- Set `AI_CHEAP_PROVIDER=openai` in .env

### When to Use Each

| Use Case | Provider | Why |
|----------|----------|-----|
| Batch filtering (1000+ items) | DeepSeek | Cache hits, quality |
| Real-time classification | GPT-4o-mini | Speed, reliability |
| Content generation | Claude Sonnet | Writing quality |
| Deep analysis | Claude Sonnet | Reasoning |

### Configuration

```env
# For batch processing (default - best margins)
AI_CHEAP_PROVIDER=deepseek

# For reliability-critical real-time ops
AI_CHEAP_PROVIDER=openai

# Auto-select based on available keys
AI_CHEAP_PROVIDER=auto
```

---

## Risk Matrix

| Risk | Impact | Mitigation |
|------|--------|------------|
| DeepSeek outage | Medium | Auto-fallback to Haiku/GPT-4o-mini |
| Claude rate limits | High | Queue system, batch processing |
| API price increases | Medium | Abstract provider interface for easy switch |
| Quality degradation | High | A/B test with user feedback scores |
| Latency spikes | Low | Async processing, user expectations set |

The current DeepSeek + Claude pairing is validated as optimal for AudienceOS.
