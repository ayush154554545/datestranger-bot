# Honest Infrastructure Cost & Free Tier Analysis

## 1. Executive Summary & Honest Warning
While initial development operates within free tier limits, **supporting 50,000+ registered users and 1,000+ concurrent active users cannot remain 100% free forever**. Infrastructure costs will scale with storage volume, database size, and worker compute.

---

## 2. Infrastructure Cost Projection Matrix

| Provider / Resource | Initial Free Tier | 10K Users Scale | 50K+ Users / 1K Concurrent Scale | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Supabase (PostgreSQL)** | Free Tier (500MB DB, 50K MAU) | Pro Tier (`$25/mo`) | Pro Tier + Compute Addon (`$25 - $75/mo`) | `VERIFY CURRENT PRICING` |
| **Redis (Upstash / Render)** | Free Tier (10K commands/day) | Pay-as-you-go (`$10 - $20/mo`) | Scaled Cache (`$30 - $60/mo`) | `VERIFY CURRENT PRICING` |
| **Cloudflare R2** | 10GB Free Storage, 10M Reads | ~50GB Storage (`$0.75/mo`) | ~500GB Storage (`$7.50/mo`) | Zero Egress Fees |
| **Bot & Worker Compute (Fly.io / Render)** | Free Web Instance | 2 Small Containers (`$14/mo`) | 4 Scaled Containers (`$35 - $70/mo`) | `VERIFY CURRENT PRICING` |
| **Next.js Website (Vercel / Cloudflare Pages)** | Free Tier | Free Tier | Free / Pro (`$0 - $20/mo`) | Static + SSR hosting |

---

## 3. Total Estimated Monthly Costs
* **Development / Launch Phase**: `$0 / month`
* **Medium Scale (10,000 Users)**: `~$50 - $80 / month`
* **Target Scale (50,000 Users / 1,000 Concurrent)**: `~$100 - $225 / month`
