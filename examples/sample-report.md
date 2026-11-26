# Cloud Cost Report — sample-account

- **Region:** us-east-1
- **Month:** 2026-10
- **Estimated monthly cost:** $788.28
- **Estimated monthly savings available:** $415.44
- **Findings:** 12

> Prices are SAMPLE prices (see pricing.py) — not live AWS pricing.

Bill total **$788.28** matches the inventory cost.

## Findings (ordered by estimated savings)

| # | Finding | Severity | Est. savings / mo |
|---|---|---|---|
| 1 | Idle instance i-gputrain01 (g5.xlarge) | HIGH | $120.72 |
| 2 | On-demand instance i-batch01 could use Spot | MEDIUM | $86.87 |
| 3 | Oversized instance i-api02 (m5.xlarge) | MEDIUM | $70.08 |
| 4 | Idle instance i-idleweb01 (m5.large) | MEDIUM | $70.08 |
| 5 | Steady-state instance i-api01 could use Reserved | MEDIUM | $28.03 |
| 6 | Old snapshot snap-001 (400 days) | LOW | $15.00 |
| 7 | Volume vol-002 is gp2 — gp3 is cheaper | LOW | $10.00 |
| 8 | Unattached volume vol-001 | LOW | $8.00 |
| 9 | Idle instance i-devbox (t3.medium) | LOW | $6.66 |
| 10 | Instance i-devbox is missing cost tags | LOW | $0.00 |
| 11 | Instance i-gputrain01 is missing cost tags | LOW | $0.00 |
| 12 | Instance i-idleweb01 is missing cost tags | LOW | $0.00 |

### 1. Idle instance i-gputrain01 (g5.xlarge)

- **Resource:** `i-gputrain01` — category `idle`
- **Monthly cost:** $120.72
- **Estimated savings:** $120.72/mo
- **Detail:** Average CPU 5%, GPU 5% over the month; monthly cost $120.72 (sample price).
- **Recommendation:** Stop or remove i-gputrain01 after confirming nothing depends on it, or downsize it to a smaller type.

### 2. On-demand instance i-batch01 could use Spot

- **Resource:** `i-batch01` — category `spot`
- **Monthly cost:** $124.10
- **Estimated savings:** $86.87/mo
- **Detail:** Fault-tolerant workload on on-demand c5.xlarge; Spot saves ~70% (sample assumption).
- **Recommendation:** Move i-batch01 to Spot instances with a diversified instance-type pool.

### 3. Oversized instance i-api02 (m5.xlarge)

- **Resource:** `i-api02` — category `oversized`
- **Monthly cost:** $140.16
- **Estimated savings:** $70.08/mo
- **Detail:** Average CPU 18% — well below the 25% oversized threshold; a m5.large would cost $70.08/mo.
- **Recommendation:** Downsize i-api02 from m5.xlarge to m5.large and watch CPU.

### 4. Idle instance i-idleweb01 (m5.large)

- **Resource:** `i-idleweb01` — category `idle`
- **Monthly cost:** $70.08
- **Estimated savings:** $70.08/mo
- **Detail:** Average CPU 4% over the month; monthly cost $70.08 (sample price).
- **Recommendation:** Stop or remove i-idleweb01 after confirming nothing depends on it, or downsize it to a smaller type.

### 5. Steady-state instance i-api01 could use Reserved

- **Resource:** `i-api01` — category `reserved`
- **Monthly cost:** $70.08
- **Estimated savings:** $28.03/mo
- **Detail:** Average CPU 65% — steady usage on on-demand m5.large; a 1-year Reserved instance saves ~40% (sample assumption).
- **Recommendation:** Buy a 1-year Reserved instance for i-api01 once the sizing is confirmed.

### 6. Old snapshot snap-001 (400 days)

- **Resource:** `snap-001` — category `snapshot`
- **Monthly cost:** $15.00
- **Estimated savings:** $15.00/mo
- **Detail:** 300 GB snapshot, 400 days old; monthly cost $15.00 (sample price).
- **Recommendation:** Confirm snap-001 is not needed for recovery, then delete it.

### 7. Volume vol-002 is gp2 — gp3 is cheaper

- **Resource:** `vol-002` — category `storage`
- **Monthly cost:** $50.00
- **Estimated savings:** $10.00/mo
- **Detail:** 500 GB gp2 at $50.00/mo; gp3 would cost $40.00/mo.
- **Recommendation:** Migrate vol-002 from gp2 to gp3.

### 8. Unattached volume vol-001

- **Resource:** `vol-001` — category `unattached`
- **Monthly cost:** $8.00
- **Estimated savings:** $8.00/mo
- **Detail:** 100 GB gp3 with no instance attached; monthly cost $8.00 (sample price).
- **Recommendation:** Snapshot vol-001 if the data is needed, then delete the volume.

### 9. Idle instance i-devbox (t3.medium)

- **Resource:** `i-devbox` — category `idle`
- **Monthly cost:** $6.66
- **Estimated savings:** $6.66/mo
- **Detail:** Average CPU 3% over the month; monthly cost $6.66 (sample price).
- **Recommendation:** Stop or remove i-devbox after confirming nothing depends on it, or downsize it to a smaller type.

### 10. Instance i-devbox is missing cost tags

- **Resource:** `i-devbox` — category `tagging`
- **Monthly cost:** $6.66
- **Estimated savings:** $0.00/mo
- **Detail:** Missing tags: cost-center. Untagged spend cannot be attributed to a team or cost centre.
- **Recommendation:** Add tags (cost-center) to i-devbox.

### 11. Instance i-gputrain01 is missing cost tags

- **Resource:** `i-gputrain01` — category `tagging`
- **Monthly cost:** $120.72
- **Estimated savings:** $0.00/mo
- **Detail:** Missing tags: cost-center. Untagged spend cannot be attributed to a team or cost centre.
- **Recommendation:** Add tags (cost-center) to i-gputrain01.

### 12. Instance i-idleweb01 is missing cost tags

- **Resource:** `i-idleweb01` — category `tagging`
- **Monthly cost:** $70.08
- **Estimated savings:** $0.00/mo
- **Detail:** Missing tags: cost-center. Untagged spend cannot be attributed to a team or cost centre.
- **Recommendation:** Add tags (cost-center) to i-idleweb01.

## Notes

- No AWS calls were made. No resources were changed.
- A human reviews every recommendation before anything is done.

