# AudienceOS - New API Endpoints Reference

## Base URL
```
http://localhost:8000/api/v1
```

---

## 🔄 Backfill Endpoints

### 1. Trigger Historical Backfill
**POST** `/backfill/{product_id}/backfill`

Starts a background task to search for and analyze historical mentions.

**Request Body:**
```json
{
  "days": 90,                          // Optional, defaults to tier limit
  "sources": ["reddit", "hackernews"]  // Optional, defaults to tier sources
}
```

**Response:**
```json
{
  "message": "Historical backfill started",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro",
  "backfill_days": 90,
  "sources": ["reddit", "hackernews"],
  "status_url": "/api/v1/backfill/task/550e8400-e29b-41d4-a716-446655440000"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/backfill/abc-123/backfill" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 90, "sources": ["reddit", "hackernews"]}'
```

---

### 2. Check Backfill Progress
**GET** `/backfill/task/{task_id}`

Monitor the progress of a backfill task.

**Response (In Progress):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "PROGRESS",
  "progress": 45,
  "stage": "reddit_backfill",
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro",
  "current_query": "task management software"
}
```

**Response (Complete):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "SUCCESS",
  "status": "completed",
  "result": {
    "product_name": "TaskMaster Pro",
    "backfill_days": 90,
    "sources": {
      "reddit": {
        "total_found": 247,
        "unique": 231,
        "in_time_range": 198,
        "relevant": 42,
        "stored": 42
      },
      "hackernews": {
        "total_found": 83,
        "unique": 79,
        "in_time_range": 67,
        "relevant": 18,
        "stored": 18
      }
    },
    "totals": {
      "total_found": 330,
      "total_relevant": 60,
      "total_stored": 60,
      "relevance_rate": 18.18
    }
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/backfill/task/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Get Product Backfill Status
**GET** `/backfill/{product_id}/status`

Check when a product was last backfilled.

**Response:**
```json
{
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro",
  "backfill_completed_at": "2026-01-25T15:30:00Z",
  "feedback_last_collected_at": "2026-01-25T18:45:00Z",
  "has_completed_backfill": true,
  "is_actively_monitored": true
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/backfill/abc-123/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔑 Keywords Endpoints

### 1. Generate Keywords
**POST** `/keywords/{product_id}/generate`

Generate keywords using AI for a product.

**Query Parameters:**
- `force_regenerate` (boolean, default: false) - Regenerate even if keywords exist

**Response:**
```json
{
  "message": "Keyword generation started",
  "task_id": "def-456",
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/keywords/abc-123/generate?force_regenerate=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Get Keywords
**GET** `/keywords/{product_id}/keywords`

Retrieve current keywords for a product.

**Response:**
```json
{
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro",
  "keywords": [
    "TaskMaster Pro",
    "TaskMaster",
    "Task Master",
    "task management software",
    "Asana alternative",
    "Trello alternative",
    "how to manage tasks",
    "team task tracking",
    "agile project management",
    "sprint planning tool"
  ],
  "keyword_count": 32,
  "competitors": [
    "Asana",
    "Trello",
    "Monday.com",
    "ClickUp",
    "Jira"
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/keywords/abc-123/keywords" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Update Keywords
**PUT** `/keywords/{product_id}/keywords`

Manually add or remove keywords.

**Request Body:**
```json
{
  "add_keywords": ["agile", "scrum", "kanban"],
  "remove_keywords": ["old-keyword"]
}
```

**Response:**
```json
{
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro",
  "action": "updated",
  "original_count": 32,
  "new_count": 34,
  "added": 3,
  "removed": 1,
  "keywords": [
    "TaskMaster Pro",
    "agile",
    "scrum",
    "kanban",
    "..."
  ]
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/v1/keywords/abc-123/keywords" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"add_keywords": ["agile", "scrum"], "remove_keywords": ["old-keyword"]}'
```

---

### 4. Analyze Keyword Coverage
**GET** `/keywords/{product_id}/keywords/analyze`

Get recommendations for improving keyword coverage.

**Response:**
```json
{
  "product_id": "abc-123",
  "product_name": "TaskMaster Pro",
  "total_keywords": 32,
  "has_brand_variations": true,
  "has_competitor_keywords": true,
  "competitor_count": 5,
  "has_problem_phrases": true,
  "recommendations": [
    "Coverage looks excellent!",
    "Consider adding more industry-specific terms"
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/keywords/abc-123/keywords/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Cache Endpoints

### 1. Get Cache Statistics
**GET** `/cache/stats`

Get cache performance metrics and cost savings.

**Response:**
```json
{
  "cache_enabled": true,
  "total_ai_cache_keys": 1250,
  "keyspace_hits": 8500,
  "keyspace_misses": 3200,
  "hit_rate": 72.64,
  "estimated_cost_savings_usd": 847.50,
  "cache_efficiency": "excellent"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/cache/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔐 Authentication

All endpoints require authentication via Bearer token:

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid sources: ['invalid']. Valid sources: ['reddit', 'hackernews']"
}
```

### 404 Not Found
```json
{
  "detail": "Product not found or access denied"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

---

## 📈 Rate Limits

- **Backfill:** 1 concurrent per product
- **Keywords Generation:** 10 per hour per product
- **Cache Stats:** 100 per minute

---

## 🎯 Usage Patterns

### Pattern 1: New Product Setup
```bash
# 1. Create product (existing endpoint)
POST /api/v1/products

# 2. Generate keywords (automatic or manual trigger)
POST /api/v1/keywords/{product_id}/generate

# 3. Trigger backfill (automatic or manual trigger)
POST /api/v1/backfill/{product_id}/backfill

# 4. Monitor progress
GET /api/v1/backfill/task/{task_id}

# 5. View results (existing endpoint)
GET /api/v1/products/{product_id}/feedback
```

### Pattern 2: Keyword Refinement
```bash
# 1. Check current keywords
GET /api/v1/keywords/{product_id}/keywords

# 2. Analyze coverage
GET /api/v1/keywords/{product_id}/keywords/analyze

# 3. Add missing keywords
PUT /api/v1/keywords/{product_id}/keywords

# 4. Re-run backfill with new keywords
POST /api/v1/backfill/{product_id}/backfill
```

### Pattern 3: Monitor Performance
```bash
# 1. Check cache efficiency
GET /api/v1/cache/stats

# 2. Check backfill status
GET /api/v1/backfill/{product_id}/status

# 3. Review keyword coverage
GET /api/v1/keywords/{product_id}/keywords/analyze
```

---

## 🧪 Testing Endpoints

### Using cURL

```bash
# Test backfill
curl -X POST "http://localhost:8000/api/v1/backfill/abc-123/backfill" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 30, "sources": ["reddit"]}'

# Test keywords
curl -X POST "http://localhost:8000/api/v1/keywords/abc-123/generate" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test cache stats
curl "http://localhost:8000/api/v1/cache/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Python

```python
import requests

base_url = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Trigger backfill
response = requests.post(
    f"{base_url}/backfill/abc-123/backfill",
    headers=headers,
    json={"days": 90, "sources": ["reddit", "hackernews"]}
)
task_id = response.json()["task_id"]

# Check progress
progress = requests.get(
    f"{base_url}/backfill/task/{task_id}",
    headers=headers
)
print(progress.json())

# Generate keywords
keywords = requests.post(
    f"{base_url}/keywords/abc-123/generate",
    headers=headers
)
print(keywords.json())

# Get cache stats
stats = requests.get(
    f"{base_url}/cache/stats",
    headers=headers
)
print(stats.json())
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Task IDs are UUIDs
- Progress percentages are 0-100
- Cache hit rates are percentages (0-100)
- Cost savings are in USD

---

**Last Updated:** January 25, 2026
