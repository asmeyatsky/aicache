# TOON Quick Reference Guide

## What is TOON?

**TOON (Token Optimization Object Notation)** is a structured data format that captures the complete optimization context for every cache operation in aicache.

Think of it as a "receipt" for each cache interaction that shows:
- **Tokens saved** (and cost savings)
- **Optimization effectiveness** (was this a good cache hit?)
- **Why the decision was made** (exact match? semantic match? why?)
- **What could improve** (suggestions for better caching)

## Quick Example

```
User Query: "What is machine learning?"
  ↓
Cache Lookup (takes 4.5ms)
  ↓
TOON Generated:
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation_type": "semantic_hit",
  "tokens": {
    "saved": {
      "total": 15,
      "percent": 100.0
    },
    "cost_saved": 0.000225  // ~0.2 thousandths of a cent
  },
  "optimization_insights": {
    "optimization_level": "high",
    "roi_score": 0.85,
    "suggested_actions": ["maintain_current_settings"]
  }
}
```

## TOON CLI Commands

### View TOON Operations
```bash
# List recent TOONs
aicache toon list [--limit=50]

# Inspect specific TOON
aicache toon inspect <operation_id>

# Get TOON of last cache operation
aicache toon last
```

### View TOON Analytics
```bash
# Show daily analytics
aicache toon analytics [--period=1d|1w|1m]

# Export analytics
aicache toon analytics --format=json

# Show recommendations
aicache toon insights
```

### Query & Filter
```bash
# Find all cache hits
aicache toon query --type=exact_hit

# Find all semantic hits
aicache toon query --type=semantic_hit

# Find high-savings operations (>100 tokens)
aicache toon query --min-tokens=100

# Find operations from last hour
aicache toon query --since=1h

# Complex query
aicache toon query --type=semantic_hit --min-tokens=50 --limit=20
```

### Export Data
```bash
# Export as JSON
aicache toon export --format=json --limit=500 > data.json

# Export as CSV (for Excel)
aicache toon export --format=csv > data.csv

# Export as JSONL (streaming)
aicache toon export --format=jsonl > data.jsonl

# Export binary (compact)
aicache toon export --format=msgpack > data.msgpack
```

### Manage TOON Data
```bash
# Delete TOON
aicache toon delete <operation_id>

# Clear old TOONs
aicache toon purge --older-than=30d

# Clear all TOONs
aicache toon clear --confirm
```

## Key TOON Concepts

### Operation Types

| Type | Meaning |
|------|---------|
| `exact_hit` | Cache matched by exact key |
| `semantic_hit` | Cache matched by similarity (AI-powered) |
| `intent_hit` | Cache matched by extracted intent |
| `exact_miss` | No cache match found |
| `semantic_miss` | Similarity too low for match |
| `cache_error` | Error during cache operation |

### Optimization Levels

| Level | Savings | Implication |
|-------|---------|------------|
| CRITICAL | ≥80% | Excellent - maintain settings |
| HIGH | 60-79% | Very good - working well |
| MEDIUM | 40-59% | Decent - consider improvements |
| LOW | 1-39% | Minimal - review strategy |
| NONE | 0% | Cache miss - add to cache |

### Key Metrics in TOON

```
tokens.saved.total          # How many tokens saved
tokens.saved.percent        # What % of tokens avoided (0-100)
tokens.cost_saved           # Dollar amount saved
optimization_level          # Quality of this cache hit
roi_score                   # Return on investment (0-1)
similarity_score            # How similar was semantic match (0-1)
cache_age_seconds           # How old is cached entry
```

## Real-World Examples

### Example 1: Perfect Cache Hit
```
Query: "What is machine learning?"
Type: exact_hit
Tokens Saved: 15 (100%)
Cost Saved: $0.000225
ROI Score: 0.95
Result: ✅ Excellent - Exact match found
```

### Example 2: Semantic Match
```
Query: "Explain machine learning concepts"
Type: semantic_hit
Tokens Saved: 12 (80%)
Cost Saved: $0.00018
Similarity: 0.92 (92% similar to cached)
ROI Score: 0.80
Result: ✅ Good - Semantic match effective
```

### Example 3: Cache Miss
```
Query: "Latest ML trends in 2024"
Type: exact_miss
Tokens Saved: 0
Cost Saved: $0.00
ROI Score: 0.0
Result: ℹ️ New query - Added to cache for future
```

## Analytics Overview

### Key Dashboard Metrics

```
Cache Performance (Last 24h)
═══════════════════════════

Hit Rate:                    87.5%
├─ Exact Hits:             65.2%
├─ Semantic Hits:          20.1%
└─ Intent Hits:             2.2%

Token Savings:             89,750 tokens
├─ Total Cost Saved:       $1.348
└─ Per Operation Avg:      71.8%

Efficiency:
├─ ROI Score:              0.718
├─ Trend:                  +0.05 (improving)
└─ Cache Efficiency:       0.85/1.0

Top Recommendations:
1. Semantic caching is working well - maintain current settings
2. Consider slightly increasing TTL for high-value entries
3. Monitor semantic threshold - no false positives detected
```

## Decision Tree: Should I Look at TOON?

```
Are you wondering...

├─ "Is my cache working?"
│  └─ Run: aicache toon analytics --period=1d
│
├─ "How much money am I saving?"
│  └─ Run: aicache toon analytics | grep "Total Cost Saved"
│
├─ "Why did a query miss the cache?"
│  └─ Run: aicache toon inspect <operation_id>
│
├─ "What's wrong with semantic caching?"
│  └─ Run: aicache toon query --type=semantic_miss --limit=10
│
├─ "Can I improve cache hit rate?"
│  └─ Run: aicache toon insights
│
└─ "Show me the details of this cache hit"
   └─ Run: aicache toon last
```

## Integration Points

TOON integrates with:

- **QueryCacheUseCase**: Generates TOON after every cache lookup
- **CacheMetrics**: Records TOON statistics automatically
- **Analytics**: Aggregates TOONs into insights
- **CLI**: Exposes TOON data via commands
- **Export**: Outputs to JSON, CSV, msgpack

## Common Patterns

### Monitor Cache Health
```bash
# Check every hour
while true; do
  aicache toon analytics --period=1h
  sleep 3600
done
```

### Alert on Poor Performance
```bash
# Alert if hit rate drops below 50%
aicache toon analytics --period=1h \
  | grep -q "Hit Rate.*[0-4][0-9]\.[0-9]%" && \
  echo "⚠️  Cache hit rate is low"
```

### Daily Report
```bash
# Generate daily report
aicache toon analytics --period=1d > daily_report.txt
aicache toon export --format=csv > daily_data.csv
git add daily_report.txt && git commit -m "Daily cache report"
```

### Cost Analysis
```bash
# Show total cost saved
aicache toon analytics | grep "Total Cost Saved"

# Export all high-value operations
aicache toon query --min-tokens=100 \
  | aicache toon export --format=csv > high_value.csv
```

## Performance Impact

TOON is designed to be lightweight:

- **Generation**: < 1ms per operation
- **Storage**: ~2KB per TOON in JSON format
- **Overhead**: < 0.1% of cache operation time
- **Automatic Cleanup**: Old TOON data auto-purged after 90 days

## File Structure

TOON data is stored locally:
```
~/.cache/aicache/
├── toon_data/
│   ├── 00/
│   ├── 01/
│   ├── ...
│   └── ff/
│       └── [operation_ids].json
└── analytics/
    └── [daily_summaries].json
```

## Privacy & Security

⚠️ **Important**: TOON objects may contain sensitive query information

- By default, queries are stored in TOON data
- Enable query sanitization: `aicache toon --sanitize-queries`
- Configure appropriate file permissions: `chmod 700 ~/.cache/aicache/toon_data`
- Regular purging recommended: `aicache toon purge --older-than=30d`

## Troubleshooting

### TOONs Not Being Generated
```bash
# Check if TOON is enabled
aicache config | grep toon.enabled

# Enable if disabled
aicache config toon.enabled=true
```

### TOON Data Storage Issues
```bash
# Check disk space
df -h ~/.cache/aicache/

# Clear old TOONs if storage is low
aicache toon purge --older-than=30d
```

### High TOON File Count
```bash
# Check how many TOONs stored
find ~/.cache/aicache/toon_data -name "*.json" | wc -l

# Compress old TOONs
aicache toon export --format=msgpack --older-than=30d > archive.msgpack
```

## Next Steps

1. **Enable TOON**: Set `toon.enabled=true` in config
2. **Check Analytics**: `aicache toon analytics --period=1d`
3. **Review Insights**: `aicache toon insights`
4. **Export Data**: `aicache toon export --format=csv`
5. **Set Up Reports**: Create daily/weekly report automation

## Learn More

- Full TOON Specification: See `docs/TOON_SPECIFICATION.md`
- Integration Guide: See `docs/TOON_INTEGRATION_GUIDE.md`
- API Documentation: See `src/aicache/domain/toon.py`
- Examples: See `tests/test_toon.py`
