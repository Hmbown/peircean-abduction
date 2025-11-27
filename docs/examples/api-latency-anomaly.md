# Example Trace: API Latency Anomaly

A complete abductive reasoning trace demonstrating how Peircean Abduction diagnoses a technical anomaly where standard metrics provide no obvious explanation.

## The Observation

```
Query: "Our API response times jumped from 50ms to 500ms overnight, but CPU, memory, and database metrics are all normal. No deployments in the last week, traffic patterns unchanged."
```

---

## Phase 1: Observation Analysis

```json
{
  "anomaly": {
    "fact": "API response times increased 10x (50ms to 500ms) overnight while CPU, memory, and database metrics remained within normal parameters",
    "surprise_level": "high",
    "surprise_score": 0.85,
    "expected_baseline": "Response time degradation typically correlates with resource utilization spikes (CPU, memory, database load) or deployment changes",
    "domain": "technical",
    "context": [
      "No deployments in the last week",
      "Traffic patterns unchanged"
    ],
    "key_features": [
      "10x latency increase without corresponding resource utilization",
      "Overnight occurrence suggests time-based or external trigger",
      "Standard observability metrics show no anomalies",
      "Decoupling between performance degradation and typical indicators"
    ],
    "surprise_source": "Violates the causal expectation that latency spikes correlate with measurable resource constraints. The absence of deployment changes and stable traffic eliminates the two most common explanatory factors, leaving a significant explanatory gap.",
    "recommended_council": [
      "Network Engineer",
      "Site Reliability Engineer",
      "Security Analyst",
      "Platform/Infrastructure Engineer",
      "Application Performance Specialist"
    ]
  }
}
```

**Peirce's First Premise**: "The surprising fact is observed: API latency increased 10x overnight with no corresponding change in CPU, memory, database, traffic, or deployments."

---

## Phase 2: Hypothesis Generation

### H1: External Service Degradation

**Statement**: An external service or API dependency has degraded, causing synchronous blocking calls to wait longer before returning

**Explanation**: External service latency would add directly to response time without consuming local CPU/memory, as the application threads simply wait on I/O

**Prior Probability**: 0.40

**Assumptions**:
- The API makes synchronous calls to external services
- External service degradation occurred overnight

**Testable Predictions**:
- Distributed tracing shows increased latency in external service spans
- External service status pages show incidents starting overnight

---

### H2: DNS Resolution Latency

**Statement**: DNS resolution latency has increased due to DNS server issues or cache expiration

**Explanation**: DNS lookups occur outside application resource metrics but add directly to connection establishment time for each request

**Prior Probability**: 0.25

**Assumptions**:
- DNS caching TTL expired or DNS server became slow
- Application makes DNS lookups per request or connection

**Testable Predictions**:
- Direct DNS query timing shows >400ms resolution times
- Bypassing DNS with direct IP addresses restores normal latency

---

### H3: Network Path Degradation

**Statement**: Network path degradation (increased hops, congestion, or routing change) is adding latency between services

**Explanation**: Network-layer latency manifests as I/O wait time, invisible to CPU/memory metrics but directly adding to response times

**Prior Probability**: 0.20

**Assumptions**:
- Network routing or infrastructure changed overnight
- The added latency is in the network path, not application code

**Testable Predictions**:
- Traceroute shows new hops or increased hop latency compared to baseline
- TCP connection establishment time (SYN-ACK) has increased

---

### H4: TLS Certificate Validation Issues

**Statement**: TLS certificate validation is failing and triggering OCSP/CRL checks or retry loops

**Explanation**: Certificate validation and revocation checks are network I/O operations that don't consume CPU/memory but block request completion

**Prior Probability**: 0.15

**Assumptions**:
- A certificate in the chain expired or was revoked overnight
- OCSP responders or CRL endpoints are slow or unreachable

**Testable Predictions**:
- SSL handshake timing shows significant delay in certificate validation phase
- Certificate chain shows expired intermediate or OCSP endpoint timeouts

---

### H5: Scheduled Job Lock Contention

**Statement**: A scheduled job or cron task is holding database locks or connection pool resources during the affected period

**Explanation**: Lock contention causes request threads to wait without consuming CPU, and connection pool exhaustion shows as I/O wait, not resource utilization

**Prior Probability**: 0.30

**Assumptions**:
- A batch job runs overnight and acquires long-held locks
- The latency spike timing correlates with job execution

**Testable Predictions**:
- Database shows long-running queries or lock waits during the spike period
- Latency spike timing exactly matches cron job schedule

---

## Phase 3: Evaluation (Council of Critics)

### The Council's Analysis

| Critic | Analysis | Verdict |
|--------|----------|---------|
| **Empiricist** | H1 and H5 have highest empirical plausibility. The decoupling of latency from resource metrics strongly suggests I/O-bound waiting. H2 and H4 are testable within minutes. | H1 most consistent with overnight timing |
| **Logician** | All hypotheses internally consistent. H1 requires fewest assumptions. H4 relies on unusual failure mode (slowdown vs. failure). | H1 is most parsimonious |
| **Pragmatist** | H1 leads to immediate action: check status pages and traces. H2 is trivially testable with `dig`. | H1 and H2 most actionable |
| **Economist** | Testing priority: H2 (30s), H1 (2min), H4 (1min), H5 (5min), H3 (needs baseline). | Test H2 first, then H1 |
| **Skeptic** | H1 weakness: "external service" is vague. H5 partially contradicted by normal DB metrics. | H1 needs specificity |

### IBE Scoring

| Criterion | H1: External | H2: DNS | H3: Network | H4: TLS | H5: Cron Job |
|-----------|--------------|---------|-------------|---------|--------------|
| Empiricist | 0.85 | 0.70 | 0.55 | 0.60 | 0.65 |
| Logician | 0.80 | 0.85 | 0.75 | 0.70 | 0.75 |
| Pragmatist | 0.90 | 0.95 | 0.60 | 0.80 | 0.70 |
| Economist | 0.75 | 0.95 | 0.50 | 0.85 | 0.65 |
| Skeptic | 0.70 | 0.65 | 0.60 | 0.55 | 0.50 |
| **COMPOSITE** | **0.80** | **0.82** | **0.60** | **0.70** | **0.65** |

---

## Selection: Inference to the Best Explanation

**Ranking**: H2 > H1 > H4 > H5 > H3

**Verdict**: **Investigate** (confidence: 0.72)

**Rationale**:
H1 (external service degradation) is the most likely root cause given the symptom pattern, but H2 (DNS) should be tested FIRST due to trivial verification cost. The overnight timing and I/O-wait-without-CPU pattern strongly suggest external dependency issues.

**Key Insight**: While H1 has higher prior probability (0.40 vs 0.25), the Council's Economist perspective elevates H2 in the investigation order because it can be ruled out in 30 seconds. This demonstrates the value of multi-perspective evaluation.

---

## Recommended Actions

1. **Immediate (30 seconds)**: Rule out DNS
   ```bash
   dig @<dns-server> <api-hostname>
   # If resolution time > 400ms, H2 is confirmed
   ```

2. **Quick check (2 minutes)**: Check external dependencies
   ```bash
   # Check status pages of all API dependencies
   # Look for incidents starting overnight
   ```

3. **Investigate (5 minutes)**: Distributed tracing
   ```bash
   # Examine traces for the API endpoint
   # Look for spans with increased latency
   # Identify which external call is slow
   ```

4. **Verify TLS (1 minute)**: Check certificate chain
   ```bash
   openssl s_client -connect <host>:443 -servername <host> 2>/dev/null | \
     openssl x509 -noout -dates
   ```

5. **If H1-H4 eliminated**: Correlate with cron schedules
   ```bash
   # Check cron logs for jobs starting at anomaly onset
   # Query pg_stat_activity for blocking queries
   ```

---

## Alternative Path

If H1 is falsified (tracing shows all external calls are fast):

**Next hypothesis to test**: H5 (Scheduled Job Lock Contention)

**Rationale**: The "overnight" trigger strongly suggests a time-based cause. If external dependencies are healthy, investigate internal scheduled processes.

**Test**:
```sql
-- Check for lock waits (PostgreSQL)
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.query AS blocked_query
FROM pg_locks blocked_locks
JOIN pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid;
```

---

## Peirce's Conclusion

> "Hence, there is reason to suspect that an external service dependency has degraded, causing synchronous I/O waits that manifest as latency without consuming local compute resources. The recommended investigation sequence prioritizes cost-effective elimination of simpler hypotheses before committing to deeper analysis."

This is a *hypothesis*, not a certainty. The recommended actions are designed to test and verify before taking corrective action.

---

## Key Takeaways

1. **Invisible I/O**: When latency increases without CPU/memory changes, look for I/O-bound waits (network, DNS, external services, locks).

2. **Cost-Effective Testing**: The Council's Economist perspective ensures you test cheap hypotheses first, even if they have lower prior probability.

3. **Overnight Trigger**: Time-based anomalies often indicate scheduled jobs, certificate expirations, or changes in external service behavior during off-hours.

4. **Observability Gaps**: Standard metrics (CPU, memory, DB) don't capture network-layer issues, DNS, or external service health.
